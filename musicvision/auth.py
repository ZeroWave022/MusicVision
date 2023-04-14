import time
import json
from flask import Blueprint, render_template, redirect, session, request, g
from musicvision import spotify_app
from musicvision.spotify import SpotifyUser
from musicvision.db import query_db, fetch_db

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

    db_user = fetch_db("SELECT * FROM users WHERE id = %s", "one", [user_info["id"]])

    # If a user already exists in the database, delete the entry
    if db_user:
        query_db(
            """
            DELETE FROM users
            WHERE id = %s
            """,
            [user_info["id"]],
        )

    query_db(
        """
        INSERT INTO users
        VALUES (%(id)s, %(access_token)s, %(token_type)s, %(scope)s, %(refresh_token)s, %(expires_at)s)
        """,
        user_info,
    )

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
