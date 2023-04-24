from datetime import datetime, timedelta
import logging
from flask import Blueprint, render_template, redirect, session
from musicvision import spotify_app
from musicvision.db import DBSession, UserAuth, select

general_bp = Blueprint("general", __name__)


@general_bp.before_app_request
def check_token_refresh():
    access_token = session.get("access_token")

    if not access_token:
        return

    db = DBSession()
    query = select(UserAuth).where(UserAuth.access_token == access_token)
    user_auth = db.scalars(query).first()

    if not user_auth:
        db.close()
        return session.clear()

    # Check if token refresh is needed
    if not user_auth.expires_at < datetime.utcnow():
        return

    refreshed_info = spotify_app.refresh_token(user_auth.refresh_token)

    if "access_token" not in refreshed_info:
        logging.warn(
            f"No access token in refreshed info from the Spotify API for {user_auth.id}. Forcing client session reset."
        )
        return session.clear()

    # Add new info to user_auth dict, which later will be sent to the database
    user_auth.access_token = refreshed_info["access_token"]
    user_auth.expires_at = datetime.utcnow() + timedelta(
        seconds=refreshed_info["expires_in"]
    )

    if "refresh_token" in refreshed_info:
        user_auth.refresh_token = refreshed_info["refresh_token"]

    session.clear()
    session["access_token"] = user_auth.access_token

    db.commit()
    db.close()


@general_bp.route("/")
def index():
    return render_template("index.html")


@general_bp.route("/features")
def features():
    return redirect("/")


@general_bp.route("/about")
def about():
    return redirect("/")
