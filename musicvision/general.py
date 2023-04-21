from datetime import datetime, timedelta
import logging
from flask import Blueprint, render_template, redirect, session
from musicvision import spotify_app
from musicvision.db import DBSession, User, UserAuth, select, update

general_bp = Blueprint("general", __name__)


@general_bp.before_app_request
def check_token_refresh():
    user = session.get("user")

    if not user:
        return

    try:
        expires_at = user["expires_at"]
    except:
        logging.warning(
            "User dict for %s is corrupted. Key 'expires_at' is not available. Resetting.",
            user["access_token"],
        )
        return session.clear()

    # Check if token refresh is needed
    if not user_auth.expires_at < datetime.utcnow():
        return

    query = select(UserAuth).where(UserAuth.access_token == user["access_token"])

    db = DBSession()
    user_auth = db.scalars(query).first()

    if not user_auth:
        db.close()
        return session.clear()

    refreshed_info = spotify_app.refresh_token(user_auth.refresh_token)

    # Add new info to user_auth dict, which later will be sent to the database
    user_auth.access_token = refreshed_info["access_token"]
    user_auth.expires_at = datetime.utcnow() + timedelta(
        seconds=refreshed_info["expires_in"]
    )

    if "refresh_token" in refreshed_info:
        user_auth.refresh_token = refreshed_info["refresh_token"]

    session.clear()
    session["user"] = {
        "access_token": user_auth.access_token,
        "expires_at": user_auth.expires_at,
    }

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
