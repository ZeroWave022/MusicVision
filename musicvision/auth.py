import json
import requests
import time
from base64 import b64encode
from flask import Blueprint, render_template, redirect, make_response, request
from musicvision.db import get_db_connection
from musicvision.env import getenv

with open("./spotify_links.json") as f:
    SPOTIFY_LINKS = json.load(f)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_b64_auth_header(client_id, client_secret):
    auth = f"{client_id}:{client_secret}".encode()
    return f"{b64encode(auth).decode()}"


def refresh_token(old_token: str) -> dict:
    req_params = {"grant_type": "refresh_token", "refresh_token": old_token}
    req_headers = {
        "Authorization": f"Basic {get_b64_auth_header(getenv('client_id'), getenv('client_secret'))}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    req = requests.post(
        SPOTIFY_LINKS["token"] + "?grant_type=refresh_token",
        params=req_params,
        headers=req_headers,
    )

    res = json.loads(req.text)

    return res


@auth_bp.route("/callback")
def auth_callback():
    args = request.args
    if "error" in args:
        return

    api_link = SPOTIFY_LINKS["token"]
    grant_type = "authorization_code"
    code = args["code"]
    redirect_uri = request.base_url

    req_headers = {
        "Authorization": f"Basic {get_b64_auth_header(getenv('client_id'), getenv('client_secret'))}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    req_params = {
        "grant_type": grant_type,
        "code": code,
        "redirect_uri": redirect_uri,
    }

    token_req = requests.post(api_link, params=req_params, headers=req_headers)

    user_info = json.loads(token_req.text)

    user_info["expires_at"] = round(time.time() + user_info["expires_in"])

    user_headers = {
        "Authorization": f"Bearer {user_info['access_token']}",
        "Content-Type": "application/json",
    }

    profile_req = requests.get(SPOTIFY_LINKS["current_user"], headers=user_headers)
    user_profile = json.loads(profile_req.text)
    user_info["id"] = user_profile["id"]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users
                VALUES (%(id)s, %(access_token)s, %(token_type)s, %(scope)s, %(refresh_token)s, %(expires_at)s)
                """,
                user_info,
            )

        conn.commit()

    response = make_response(redirect("/"))
    response.set_cookie("logged_in", "1")
    response.set_cookie("access_token", user_info["access_token"])
    return response


@auth_bp.route("/login")
def login():
    api_link = SPOTIFY_LINKS["login"]
    client_id = getenv("client_id")
    redirect_uri = request.host_url + "auth/callback"
    state = ""  # TBA
    scope = getenv("scope")

    auth_link = f"{api_link}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"

    return render_template("login.html", auth_link=auth_link)
