from flask import Blueprint, abort, session
from musicvision.spotify import SpotifyUser

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.post("/toggle_player")
def toggle_player():
    if not session.get("user"):
        return abort(401)

    user = SpotifyUser(session["user"]["access_token"])

    player = user.get_currently_playing()
    toggled = not player["is_playing"]
    if player:
        success = user.toggle_playback(toggled)
    else:
        success = False

    # Set status if change was successful
    # Set isPlaying to the new status if successful, otherwise provide the old status
    return {
        "status": "success" if success else "failed",
        "isPlaying": toggled if success else player["is_playing"],
    }
