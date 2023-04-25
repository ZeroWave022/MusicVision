from flask import Blueprint, abort, session, request
from musicvision.spotify import SpotifyUser
from musicvision.db import DBSession, User, UserAuth, Artist, Track, select

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.before_request
def require_token():
    if not session.get("access_token"):
        return abort(401)


@api_bp.post("/toggle-player")
def toggle_player():
    user = SpotifyUser(session["access_token"])

    player = user.get_currently_playing()
    toggled = not player["is_playing"]
    if player:
        success = user.toggle_playback(toggled)
    else:
        success = False

    # Set status if change was successful
    # Set isPlaying to the new status if successful, otherwise provide the old status
    return {
        "status": "success" if success else "failed",
        "isPlaying": toggled if success else player["is_playing"],
    }


@api_bp.get("/artist/<string:id>")
def get_one_artist(id):
    token = session["access_token"]
    options = request.args

    with DBSession() as db:
        user = db.scalar(select(UserAuth).where(UserAuth.access_token == token))

    if not user:
        session.clear()
        return abort(401)

    spotify = SpotifyUser(user.access_token)

    try:
        api_artist_data = spotify.get_artist(id)
    except:
        return abort(400)

    # Set up an artist_info dictionary which will be returned from this endpoint
    artist_info = {
        "id": id,
        "name": api_artist_data["name"],
        "url": api_artist_data["external_urls"]["spotify"],
        "image": api_artist_data["images"][0]["url"],
    }

    if "time_frame" not in options:
        return artist_info

    time_frame = options["time_frame"]

    with DBSession() as db:
        query = select(Artist).where(
            Artist.artist_id == id,
            Artist.user_id == user.id,
            Artist.time_frame == time_frame,
        )
        artist_data = db.scalars(query).all()

    # If there's no DB data to add, send general artist info only
    if len(artist_data) == 0:
        return artist_info

    # Go through data and assign popularities and timestamps
    popularities = []
    timestamps = []

    for data in artist_data:
        popularities.append(data.popularity)
        formatted_time = data.added_at.strftime("%d %B %Y, %H:%M")
        timestamps.append(formatted_time)

    artist_info.update(
        {
            "chart_data": {
                "timestamps": timestamps,
                "popularities": popularities,
                "time_frame": time_frame,
            }
        }
    )

    return artist_info


@api_bp.get("/track/<string:id>")
def get_one_track(id):
    token = session["access_token"]
    options = request.args

    with DBSession() as db:
        user = db.scalar(select(UserAuth).where(UserAuth.access_token == token))

    if not user:
        session.clear()
        return abort(401)

    spotify = SpotifyUser(user.access_token)

    try:
        api_track_data = spotify.get_track(id)
    except:
        return abort(400)

    # Set up a track_info dictionary which will be returned from this endpoint
    track_info = {
        "id": id,
        "artists": [artist["name"] for artist in api_track_data["artists"]],
        "name": api_track_data["name"],
        "url": api_track_data["external_urls"]["spotify"],
        "image": api_track_data["album"]["images"][0]["url"],
    }

    if "time_frame" not in options:
        return track_info

    time_frame = options["time_frame"]

    # Get track data for this time_frame
    with DBSession() as db:
        query = select(Track).where(
            Track.track_id == id,
            Track.user_id == user.id,
            Track.time_frame == time_frame,
        )
        track_data = db.scalars(query).all()

    # If there's no DB data to add, send general track info only
    if len(track_data) == 0:
        return track_info

    # Go through data and assign popularities and timestamps
    popularities = []
    timestamps = []

    for data in track_data:
        popularities.append(data.popularity)
        formatted_time = data.added_at.strftime("%d %B %Y, %H:%M")
        timestamps.append(formatted_time)

    track_info.update(
        {
            "chart_data": {
                "timestamps": timestamps,
                "popularities": popularities,
                "time_frame": time_frame,
            }
        }
    )

    return track_info


@api_bp.get("/top/tracks")
def top_tracks():
    token = session["access_token"]
    options = request.args

    if "time_frame" not in options:
        return abort(400)

    with DBSession() as db:
        user = db.scalar(select(UserAuth).where(UserAuth.access_token == token))

        query = select(Track).where(
            Track.user_id == user.id, Track.time_frame == options["time_frame"]
        )

        try:
            limit = int(options["limit"]) if int(options["limit"]) <= 15 else 5
        except:
            limit = 5

        all_tracks = db.scalars(query).all()
        all_tracks = sorted(all_tracks, key=lambda i: i.popularity, reverse=True)

        unique_ids = []

        for track in all_tracks:
            if track.track_id not in unique_ids:
                unique_ids.append(track.track_id)

        unique_ids = unique_ids[:limit]

        api_tracks = SpotifyUser(token).get_tracks(unique_ids)["tracks"]

        ready_tracks = []

        for track_id in unique_ids:
            # Reuse query, but only get rows for this track
            track_data = db.scalars(query.where(Track.track_id == track_id)).all()

            popularities = []
            timestamps = []

            for data in track_data:
                popularities.append(data.popularity)
                formatted_time = data.added_at.strftime("%d %B %Y, %H:%M")
                timestamps.append(formatted_time)

            api_track = [track for track in api_tracks if track["id"] == track_id][0]

            if len(api_track["artists"]) > 1:
                track_full_name = f"{api_track['artists'][0]['name']} and more... - {api_track['name']}"
            else:
                track_full_name = (
                    f"{api_track['artists'][0]['name']} - {api_track['name']}"
                )

            ready_tracks.append(
                {
                    "id": track_id,
                    "name": track_full_name,
                    "timestamps": timestamps,
                    "popularities": popularities,
                }
            )

        return ready_tracks


@api_bp.get("/top/artists")
def top_artists():
    token = session["access_token"]
    options = request.args

    if "time_frame" not in options:
        return abort(400)

    with DBSession() as db:
        user = db.scalar(select(UserAuth).where(UserAuth.access_token == token))

        query = select(Artist).where(
            Artist.user_id == user.id, Artist.time_frame == options["time_frame"]
        )

        try:
            limit = int(options["limit"]) if int(options["limit"]) <= 15 else 5
        except:
            limit = 5

        all_artists = db.scalars(query).all()
        all_artists = sorted(all_artists, key=lambda i: i.popularity, reverse=True)

        unique_ids = []

        for artist in all_artists:
            if artist.artist_id not in unique_ids:
                unique_ids.append(artist.artist_id)

        unique_ids = unique_ids[:limit]

        api_artists = SpotifyUser(token).get_artists(unique_ids)["artists"]

        ready_artists = []

        for artist_id in unique_ids:
            # Reuse query, but only get rows for this track
            track_data = db.scalars(query.where(Artist.artist_id == artist_id)).all()

            popularities = []
            timestamps = []

            for data in track_data:
                popularities.append(data.popularity)
                formatted_time = data.added_at.strftime("%d %B %Y, %H:%M")
                timestamps.append(formatted_time)

            api_artist = [
                artist for artist in api_artists if artist["id"] == artist_id
            ][0]

            ready_artists.append(
                {
                    "id": artist_id,
                    "name": api_artist["name"],
                    "timestamps": timestamps,
                    "popularities": popularities,
                }
            )

        return ready_artists
