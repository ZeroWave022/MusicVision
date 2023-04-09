import time
from flask import Blueprint, render_template, redirect, session
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


@general_bp.route("/features")
def features():
    return redirect("/")


@general_bp.route("/about")
def about():
    return redirect("/")
