from datetime import datetime, timedelta
import threading
import time
import logging
from sqlalchemy.orm import Session
from musicvision import spotify_app
from musicvision.db import DBSession, User, UserAuth, Artist, Track, select
from musicvision.spotify import SpotifyUser


def _update_access_token(user: User) -> None:
    """Add new access token for this user's auth.
    It is expected that the `session` is open during the execution of this procedure.
    Commiting and closing the session are tasks which must be handled outside this procedure.

    For interal use only (within `musicvision.tasks`).
    """
    refreshed_info = spotify_app.refresh_token(user.auth.refresh_token)

    # Add new info to user_auth dict, which later will be sent to the database
    user.auth.access_token = refreshed_info["access_token"]
    user.auth.expires_at = datetime.utcnow() + timedelta(
        seconds=refreshed_info["expires_in"]
    )

    if "refresh_token" in refreshed_info:
        user.auth.refresh_token = refreshed_info["refresh_token"]


def _add_tracks(session: Session, user: User, time_frames: list[str] = None) -> None:
    """Add new values for top tracks for this user.
    It is expected that the `session` is open during the execution of this procedure.
    Commiting and closing the session are tasks which must be handled outside this procedure.

    For interal use only (within `musicvision.tasks`).
    """
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
                user_id=user.id,
                track_id=track["id"],
                time_frame=time_frame,
                popularity=track["popularity"],
            )
            new_tracks.append(db_track)

        session.add_all(new_tracks)


def _add_artists(session: Session, user: User, time_frames: list[str] = None) -> None:
    """Add new values for top artists for this user.
    It is expected that the `session` is open during the execution of this procedure.
    Commiting and closing the session are tasks which must be handled outside this procedure.

    For interal use only (within `musicvision.tasks`).
    """
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
                user_id=user.id,
                artist_id=artist["id"],
                time_frame=time_frame,
                popularity=artist["popularity"],
            )
            new_artists.append(db_artist)

        session.add_all(new_artists)


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

    _add_tracks(session, db_auth.user)
    _add_artists(session, db_auth.user)

    session.commit()
    session.close()


def _check_user_data() -> None:
    while True:
        session = DBSession()
        all_users = session.scalars(select(User)).all()

        for user in all_users:
            # Next update is at the last update + 6 hours
            now = datetime.utcnow()
            next_update_at = user.last_updated + timedelta(hours=6)

            if now < next_update_at:
                continue

            if user.auth.expires_at < now:
                _update_access_token(user)

            _add_tracks(session, user)
            _add_artists(session, user)

            user.last_updated = now

        session.commit()
        session.close()

        time.sleep(600)  # Check every 10 minutes


def start_tasks():
    all_tasks = [_check_user_data]
    for task in all_tasks:
        thread = threading.Thread(target=task, name=task.__name__, daemon=True)
        thread.start()
