import json
import time
import requests
from flask import Blueprint, render_template, make_response, request
from musicvision.auth import refresh_token
from musicvision.db import query_db, fetch_db

with open("./spotify_links.json") as f:
    SPOTIFY_LINKS = json.load(f)

general_bp = Blueprint("general", __name__)

@general_bp.route("/")
def index():
    if request.cookies.get("logged_in") == "1":
        current_token = request.cookies.get("access_token")
        
        """with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE access_token = %s", [current_token])

                current_user = cur.fetchone()"""
        
        current_user = fetch_db("SELECT * FROM users WHERE access_token = %s", "one", [current_token])

        token_refresh_required = current_user["expires_at"] < time.time()

        if token_refresh_required:
            refreshed = refresh_token(current_user["refresh_token"])
            
            current_user["old_token"] = current_user["access_token"]
            current_user["access_token"] = refreshed["access_token"]
            current_user["expires_at"] = round(time.time() + refreshed["expires_in"])
            
            new_refresh_token = refreshed.get("refresh_token")
            if new_refresh_token:
                current_user["refresh_token"] = refreshed["refresh_token"]

            """with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE users
                        SET access_token=%(access_token)s, refresh_token=%(refresh_token)s, expires_at=%(expires_at)s
                        WHERE access_token=%(old_token)s
                    ''', current_user)
                
                conn.commit()"""

            query_db("""
                UPDATE users
                SET access_token=%(access_token)s, refresh_token=%(refresh_token)s, expires_at=%(expires_at)s
                WHERE access_token=%(old_token)s
                """, current_user)
        
        req_headers = {
            "Authorization": f"Bearer {request.cookies.get('access_token')}"
        }
        req = requests.get(SPOTIFY_LINKS["current_user"], headers=req_headers)
        data = json.loads(req.text)

        template = render_template("index.html", name=data["display_name"], followers=data["followers"]["total"])
        response = make_response(template)
        
        if token_refresh_required:
            response.set_cookie("access_token", current_user["access_token"])
        
        return response
    else:
        return render_template("index.html")
