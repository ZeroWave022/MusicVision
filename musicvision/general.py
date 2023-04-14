import time
import logging
from flask import Blueprint, render_template, redirect, session
from musicvision import spotify_app
from musicvision.db import User

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
            user["id"],
        )
        return session.clear()

    # Check if token refresh is needed
    if not expires_at < time.time():
        return

    try:
        current_user: User = User.get(User.access_token == user["access_token"])
    except:
        return session.clear()

    refreshed_info = spotify_app.refresh_token(current_user["refresh_token"])

    # Add new info to current_user dict, which later will be sent to the database
    current_user.access_token = refreshed_info["access_token"]
    current_user.expires_at = round(time.time() + refreshed_info["expires_in"])

    if "refresh_token" in refreshed_info:
        current_user.refresh_token = refreshed_info["refresh_token"]

    current_user.save()

    session.clear()
    session["user"] = current_user


@general_bp.route("/")
def index():
    return render_template("index.html")


@general_bp.route("/features")
def features():
    return redirect("/")


@general_bp.route("/about")
def about():
    return redirect("/")
