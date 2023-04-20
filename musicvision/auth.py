import time
from datetime import datetime
import json
from threading import Thread
from flask import Blueprint, render_template, redirect, session, request, g
from musicvision import spotify_app
from musicvision.spotify import SpotifyUser
from musicvision.db import DBSession, User, UserAuth, select
from musicvision.tasks import setup_new_user

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

    is_new_user = False

    # Update user and their auth if already in database, otherwise create a new entry
    with DBSession() as db:
        user_query = select(User).where(User.id == user_info["id"])
        db_user = db.scalars(user_query).first()

        # If there's already a user, update the row
        # Otherwise add a row and set is_new_user
        if db_user:
            db_user.last_logged_in = datetime.utcnow()
        else:
            db_user = User(id=user_info["id"])
            db.add(db_user)
            is_new_user = True

        # If there's already a user auth for this user, update it, otherwise add a row
        auth = db_user.auth

        if auth:
            auth.access_token = user_info["access_token"]
            auth.scope = user_info["scope"]
            auth.refresh_token = user_info["refresh_token"]
            auth.expires_at = user_info["expires_at"]
        else:
            new_auth = UserAuth(
                id=user_info["id"],
                access_token=user_info["access_token"],
                token_type=user_info["token_type"],
                scope=user_info["scope"],
                refresh_token=user_info["refresh_token"],
                expires_at=user_info["expires_at"],
            )
            db.add(new_auth)

        db.commit()

    # If a new user has registered, perform a manual update of their data in a thread
    if is_new_user:
        user_thread = Thread(target=setup_new_user, args=(user_info["access_token"],))
        user_thread.start()

    # Clear the session of any old data and insert new
    session.clear()
    session["user"] = {
        "access_token": user_info["access_token"],
        "expires_at": user_info["expires_at"],
    }

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
