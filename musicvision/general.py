import time
from flask import Blueprint, render_template, redirect, url_for, session
from musicvision import spotify_app
from musicvision.spotify import SpotifyUser
from musicvision.db import query_db, fetch_db

general_bp = Blueprint("general", __name__)


@general_bp.route("/")
def index():
    user = session.get("user")

    if not user:
        return render_template("index.html")

    current_user = fetch_db(
        "SELECT * FROM users WHERE access_token = %s", "one", [user["access_token"]]
    )

    token_refresh_required = current_user["expires_at"] < time.time()

    if token_refresh_required:
        refreshed = spotify_app.refresh_token(current_user["refresh_token"])

        current_user["old_token"] = current_user["access_token"]
        current_user["access_token"] = refreshed["access_token"]
        current_user["expires_at"] = round(time.time() + refreshed["expires_in"])

        new_refresh_token = refreshed.get("refresh_token")
        if new_refresh_token:
            current_user["refresh_token"] = refreshed["refresh_token"]

        query_db(
            """
            UPDATE users
            SET access_token=%(access_token)s, refresh_token=%(refresh_token)s, expires_at=%(expires_at)s
            WHERE access_token=%(old_token)s
            """,
            current_user,
        )

    user = SpotifyUser(current_user["access_token"])
    profile = user.get_profile()

    if token_refresh_required:
        session["user"] = current_user

    return render_template(
        "index.html",
        name=profile["display_name"],
        followers=profile["followers"]["total"],
    )


@general_bp.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    access_token = session["user"]["access_token"]
    user = SpotifyUser(access_token)
    player = user.get_currently_playing()

    if not player:
        return render_template("dashboard.html")

    song = player["item"]

    all_artists = [artist["name"] for artist in song["artists"]]
    song["all_artists"] = ", ".join(all_artists)

    try:
        song_in_playlist = player["context"]["type"] == "playlist"
    except:
        song_in_playlist = False

    if song_in_playlist:
        # The playlist id is the last part of the API URL
        id = player["context"]["href"].split("/")[-1]
        playlist = user.get_playlist(id)

        song["playlist"] = {
            "name": playlist["name"],
            "url": playlist["external_urls"]["spotify"],
        }

    return render_template("dashboard.html", song=song, is_playing=player["is_playing"])


@general_bp.route("/top_artists")
def top_artists():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    user = SpotifyUser(session["user"]["access_token"])
    artists_raw = user.get_top("artists", "medium_term", 25)
    artists = artists_raw["items"]

    for artist in artists:
        artist["genres"] = [i.capitalize() for i in artist["genres"]]
        artist["genres"] = ", ".join(artist["genres"][:3])

    artists_sorted = sorted(
        artists_raw["items"], key=lambda i: i["popularity"], reverse=True
    )

    return render_template("top_artists.html", artists=enumerate(artists_sorted))


@general_bp.route("/top_tracks")
def top_tracks():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    user = SpotifyUser(session["user"]["access_token"])
    tracks_raw = user.get_top("tracks", "medium_term", 25)

    tracks = tracks_raw["items"]
    tracks = sorted(tracks, key=lambda i: i["popularity"], reverse=True)

    return render_template("top_tracks.html", tracks=enumerate(tracks))
