import time
import json
from flask import Blueprint, render_template, redirect, session, request, g
from musicvision import spotify_app
from musicvision.spotify import SpotifyUser
from musicvision.db import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

with open("config.json") as f:
    config = json.load(f)


@auth_bp.before_app_request
def load_logged_in_user():
    user = session.get("user")

    if user:
        g.user = user
    else:
        g.user = None


@auth_bp.route("/callback")
def auth_callback():
    args = request.args
    if "error" in args:
        return

    code = args["code"]

    # Get user info and set when token expires
    user_info = spotify_app.get_user_token(code, request.base_url)

    user_info["expires_at"] = round(time.time() + user_info["expires_in"])

    # Get user profile and add their id to their info
    user = SpotifyUser(user_info["access_token"])
    user_profile = user.get_profile()

    user_info["id"] = user_profile["id"]

    # Update user if already in database, otherwise create a new entry
    try:
        db_user = User.get(User.id == user_info["id"])

        db_user.access_token = user_info["access_token"]
        db_user.scope = user_info["scope"]
        db_user.refresh_token = user_info["refresh_token"]
        db_user.expires_at = user_info["expires_at"]
    except:
        db_user: User = User.create(
            id=user_info["id"],
            access_token=user_info["access_token"],
            token_type=user_info["token_type"],
            scope=user_info["scope"],
            refresh_token=user_info["refresh_token"],
            expires_at=user_info["expires_at"],
        )

    db_user.save()

    session.clear()
    session["user"] = user_info
    return redirect("/")


@auth_bp.route("/login")
def login():
    if session.get("user"):
        return redirect("/dashboard")

    redirect_uri = request.host_url + "auth/callback"
    state = ""  # TBA
    scope = config["scope"]

    auth_link = spotify_app.gen_user_auth_link(redirect_uri, scope, state)

    return render_template("login.html", auth_link=auth_link)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
