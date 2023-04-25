from flask import Blueprint, render_template, redirect, url_for, abort, session, request
from musicvision.spotify import SpotifyUser
from musicvision.db import DBSession, User, UserAuth, select

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.before_request
def ensure_user_logged_in():
    if not session.get("access_token"):
        return redirect(url_for("auth.login"))


@dashboard_bp.route("/")
def index():
    access_token = session["access_token"]
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


@dashboard_bp.route("/top-artists")
def top_artists():
    filter = request.args.get("f")
    page = request.args.get("p", type=int)

    # If a wrong filter is specified, use the default
    if filter not in ["long_term", "medium_term", "short_term"]:
        filter = "long_term"

    # page must be a positive integer under 5 (max 50 items from API)
    if not isinstance(page, int) or page > 5 or page < 1:
        page = 1

    user = SpotifyUser(session["access_token"])

    # Decrement page by one to get correct offset
    artists_raw = user.get_top("artists", filter, 10, (page - 1) * 10)
    artists = artists_raw["items"]

    # Request these artists from the API to get their followers and additional info
    artist_ids = [artist["id"] for artist in artists]
    full_artists = user.get_artists(artist_ids)["artists"]

    for artist in artists:
        artist["genres"] = [i.capitalize() for i in artist["genres"]]
        artist["genres"] = ", ".join(artist["genres"][:3])

        # The spotify get top items endpoint doesn't return followers correctly, so these need to be retrieved from the get artists endpoint
        # Get this artist's full info and set their followers
        api_artist = [item for item in full_artists if item["id"] == artist["id"]]
        artist["followers"]["total"] = api_artist[0]["followers"]["total"]

    artists_sorted = sorted(
        artists_raw["items"], key=lambda i: i["popularity"], reverse=True
    )

    return render_template(
        "dashboard/top-artists.html",
        artists=enumerate(artists_sorted),
        filter=filter,
        page=page,
    )


@dashboard_bp.route("/top-tracks")
def top_tracks():
    filter = request.args.get("f")
    page = request.args.get("p", type=int)

    # If a wrong filter is specified, use the default
    if filter not in ["long_term", "medium_term", "short_term"]:
        filter = "long_term"

    # page must be a positive integer under 5 (max 50 items from API)
    if not isinstance(page, int) or page > 5 or page < 1:
        page = 1

    user = SpotifyUser(session["access_token"])

    # Decrement page by one to get correct offset
    tracks_raw = user.get_top("tracks", filter, 10, (page - 1) * 10)
    tracks = tracks_raw["items"]
    tracks = sorted(tracks, key=lambda i: i["popularity"], reverse=True)

    return render_template(
        "dashboard/top-tracks.html", tracks=enumerate(tracks), filter=filter, page=page
    )


@dashboard_bp.get("artist/<string:id>")
def artist(id):
    spotify = SpotifyUser(session["access_token"])

    try:
        artist = spotify.get_artist(id)
    except:
        abort(400)

    return render_template("dashboard/artist.html", artist=artist)


@dashboard_bp.get("track/<string:id>")
def track(id):
    spotify = SpotifyUser(session["access_token"])

    try:
        track = spotify.get_track(id)
    except:
        abort(400)

    artists = [artist["name"] for artist in track["artists"]]

    return render_template(
        "dashboard/track.html", track=track, formatted_artists=", ".join(artists)
    )


@dashboard_bp.get("delete-account")
def delete_account():
    user = SpotifyUser(session["access_token"])
    profile = user.get_profile()

    return render_template(
        "dashboard/delete-account.html", username=profile["display_name"]
    )


@dashboard_bp.post("delete-account")
def delete_account_post():
    token = session["access_token"]

    with DBSession() as db:
        auth_query = select(UserAuth).where(UserAuth.access_token == token)
        db_auth = db.scalars(auth_query).first()

        if not db_auth:
            session.clear()
            return redirect("/")

        # Deleting the user row is enough, as the linked UserAuth and other linked data will be deleted with it (ON DELETE CASCADE)
        try:
            db.delete(db_auth.user)
            db.commit()
        except Exception as e:
            print(e)
            return abort(500)

    session.clear()

    return render_template("dashboard/delete-account.html", deleted=True)
