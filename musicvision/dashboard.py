from flask import Blueprint, render_template, redirect, url_for, session
from musicvision.spotify import SpotifyUser

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    access_token = session["user"]["access_token"]
    user = SpotifyUser(access_token)
    player = user.get_currently_playing()

    if not player:
        return render_template("dashboard/index.html")

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

    # Check if user has premium. Play/pause API calls are locked behind premium.
    user_profile = user.get_profile()
    simple_player = {
        "enabled": user_profile.get("product") == "premium",
        "is_playing": player["is_playing"],
    }

    return render_template("dashboard/index.html", song=song, player=simple_player)


@dashboard_bp.route("/top_artists")
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

    return render_template(
        "dashboard/top_artists.html", artists=enumerate(artists_sorted)
    )


@dashboard_bp.route("/top_tracks")
def top_tracks():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    user = SpotifyUser(session["user"]["access_token"])
    tracks_raw = user.get_top("tracks", "medium_term", 25)

    tracks = tracks_raw["items"]
    tracks = sorted(tracks, key=lambda i: i["popularity"], reverse=True)

    return render_template("dashboard/top_tracks.html", tracks=enumerate(tracks))
