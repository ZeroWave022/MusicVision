import json
import time
import requests
from flask import Blueprint, render_template, redirect, session
from musicvision.auth import refresh_token
from musicvision.db import query_db, fetch_db

with open("./spotify_links.json") as f:
    SPOTIFY_LINKS = json.load(f)

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
        refreshed = refresh_token(current_user["refresh_token"])

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
            [current_user],
        )

    req_headers = {"Authorization": f"Bearer {current_user['access_token']}"}
    req = requests.get(SPOTIFY_LINKS["current_user"], headers=req_headers)
    data = json.loads(req.text)

    if token_refresh_required:
        session["user"] = current_user

    return render_template(
        "index.html",
        name=data["display_name"],
        followers=data["followers"]["total"],
    )


@general_bp.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect("/login")

    headers = {
        "Authorization": f"Bearer {session['user']['access_token']}",
        "Content-Type": "application/json",
    }

    current_song_req = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing", headers=headers
    )

    song = current_song_req.json()

    return render_template("dashboard.html", song=song)
