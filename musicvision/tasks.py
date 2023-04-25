from datetime import datetime, timedelta
import threading
import time
import logging
from sqlalchemy import update
from sqlalchemy.orm import joinedload
from musicvision import spotify_app
from musicvision.db import DBSession, User, UserAuth, Artist, Track, select
from musicvision.spotify import SpotifyUser


def _update_access_token(user: str) -> None:
    """Add new access token for this user's auth.
    Commiting and closing the session are tasks which must be handled outside this procedure.

    For interal use only (within `musicvision.tasks`).
    """
    session = DBSession()
    auth = session.scalar(select(UserAuth).where(UserAuth.id == user))
    refreshed_info = spotify_app.refresh_token(auth.refresh_token)

    # Add new info to UserAuth
    auth.access_token = refreshed_info["access_token"]
    auth.expires_at = datetime.utcnow() + timedelta(
        seconds=refreshed_info["expires_in"]
    )

    if "refresh_token" in refreshed_info:
        auth.refresh_token = refreshed_info["refresh_token"]

    session.commit()
    session.close()


def _add_tracks(user_id: str, time_frames: list[str] = None) -> None:
    """Add new values for top tracks attached to this user.
    Commiting the changes is handled within this procedure.

    For interal use only (within `musicvision.tasks`).
    """
    with DBSession() as db:
        user = db.scalar(select(User).where(User.id == user_id))
        spotify = SpotifyUser(user.auth.access_token)

    # Use the provided time frames if provided, else use all available
    all_time_frames = (
        time_frames
        if time_frames is not None
        else ["short_term", "medium_term", "long_term"]
    )

    for time_frame in all_time_frames:
        api_tracks = spotify.get_top("tracks", time_frame, 50)
        new_tracks = []

        for track in api_tracks["items"]:
            db_track = Track(
                user_id=user_id,
                track_id=track["id"],
                time_frame=time_frame,
                popularity=track["popularity"],
            )
            new_tracks.append(db_track)

        with DBSession() as db:
            db.add_all(new_tracks)
            db.commit()


def _add_artists(user_id: str, time_frames: list[str] = None) -> None:
    """Add new values for top artists attached to this user.
    Commiting the changes is handled within this procedure.

    For interal use only (within `musicvision.tasks`).
    """
    with DBSession() as db:
        user = db.scalar(select(User).where(User.id == user_id))
        spotify = SpotifyUser(user.auth.access_token)

    # Use the provided time frames if provided, else use all available
    all_time_frames = (
        time_frames
        if time_frames is not None
        else ["short_term", "medium_term", "long_term"]
    )

    for time_frame in all_time_frames:
        api_artists = spotify.get_top("artists", time_frame, 50)
        new_artists = []

        for artist in api_artists["items"]:
            db_artist = Artist(
                user_id=user_id,
                artist_id=artist["id"],
                time_frame=time_frame,
                popularity=artist["popularity"],
            )
            new_artists.append(db_artist)

        with DBSession() as db:
            db.add_all(new_artists)
            db.commit()


def setup_new_user(access_token: str) -> None:
    """Set up a new user in the database by adding their favorite artists and tracks.
    This is a manual task which needs to be invoked manually.
    """
    session = DBSession()
    query = select(UserAuth).where(UserAuth.access_token == access_token)
    db_auth = session.scalars(query).first()

    if not db_auth:
        return logging.error(
            "ABORTING setup_new_user: Asked to setup new user which wasn't found in database"
        )

    _add_tracks(db_auth.id)
    _add_artists(db_auth.id)

    session.commit()
    session.close()


def _check_user_data() -> None:
    while True:
        try:
            # Load User.auth too, as we'll need it later
            query = select(User).options(joinedload(User.auth))

            with DBSession() as db:
                all_users = db.scalars(query).all()

            now = datetime.utcnow()

            # Update access tokens if needed
            for user in all_users:
                if user.auth.expires_at < now:
                    _update_access_token(user.id)

            # Update users, as they may have new info
            with DBSession() as db:
                all_users = db.scalars(query).all()

            updated_info = []

            for user in all_users:
                # Next update is at the last update + 6 hours
                next_update_at = user.last_updated + timedelta(hours=6)

                if now < next_update_at:
                    continue

                _add_tracks(user.id)
                _add_artists(user.id)

                updated_info.append({"id": user.id, "last_updated": now})

            with DBSession() as db:
                db.execute(update(User), updated_info)
                db.commit()

            time.sleep(600)  # Check every 10 minutes
        except Exception as e:
            print("Exception raised in _check_user_data")
            print(e)
            time.sleep(60)  # If the loop encouters an exception, retry after a minute


def start_tasks():
    all_tasks = [_check_user_data]
    for task in all_tasks:
        thread = threading.Thread(target=task, name=task.__name__, daemon=True)
        thread.start()
