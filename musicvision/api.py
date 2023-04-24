from flask import Blueprint, abort, session, request
from musicvision.spotify import SpotifyUser
from musicvision.db import DBSession, UserAuth, select, Artist, Track

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.post("/toggle-player")
def toggle_player():
    if not session.get("access_token"):
        return abort(401)

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


@api_bp.get("/top/tracks")
def top_tracks():
    if not session.get("access_token"):
        return abort(401)

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
    if not session.get("access_token"):
        return abort(401)

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
