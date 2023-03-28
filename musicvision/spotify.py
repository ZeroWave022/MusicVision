import requests
import json
from base64 import b64encode

API_LINKS = {
    "login": "https://accounts.spotify.com/authorize",
    "token": "https://accounts.spotify.com/api/token",
    "current_user": "https://api.spotify.com/v1/me",
    "playback_state": "https://api.spotify.com/v1/me/player",
    "currently_playing": "https://api.spotify.com/v1/me/player/currently-playing",
    "playlist": "https://api.spotify.com/v1/playlists/",
}


def _b64_auth_header(client_id, client_secret):
    auth = f"{client_id}:{client_secret}".encode()
    return f"{b64encode(auth).decode()}"


def get_user_auth_link(
    client_id: str, redirect_uri: str, scope: str, state: str
) -> str:
    base_link = API_LINKS["login"]
    return f"{base_link}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"


def get_user_token(
    client_id: str, client_secret: str, code: str, redirect_uri: str
) -> dict:
    """Get a user's token after they have approved the app.

    Parameters
    ----------
    client_id: `str`
        Application client id
    client_secret: `str`
        Application secret id
    code: str
        The code returned from the API on the redirect URI upon authorization
    redirect_uri:
        The same redirect URI which was used for the authorization step

    Returns
    -------
    `dict`
    """

    headers = {
        "Authorization": f"Basic {_b64_auth_header(client_id, client_secret)}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    res = requests.post(API_LINKS["token"], params=params, headers=headers)

    if not res.ok or res.text == "":
        raise Exception(
            "Spotify get_user_token request failed with a non-200 status code or no content was received."
        )

    return json.loads(res.text)


def refresh_token(client_id: str, client_secret: str, old_token: str) -> dict:
    headers = {
        "Authorization": f"Basic {_b64_auth_header(client_id, client_secret)}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    params = {"grant_type": "refresh_token", "refresh_token": old_token}

    res = requests.post(
        API_LINKS["token"],
        params=params,
        headers=headers,
    )

    return json.loads(res.text)


def get_user(access_token: str) -> dict:
    """Get a user info from the Spotify API.
    Docs: https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile

    Parameters
    ----------
    access_token: `str`
        User's bearer access token

    Returns
    -------
    `dict`
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    res = requests.get(API_LINKS["current_user"], headers=headers)

    if not res.ok or res.text == "":
        raise Exception(
            "Spotify get_user request failed with a non-200 status code or no content was received."
        )

    return json.loads(res.text)


def get_playback_state(access_token: str):
    """Get playback state for user.
    Docs: https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback

    Parameters
    ----------
    access_token: `str`
        User's bearer access token

    Returns
    -------
    `dict`
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    res = requests.get(API_LINKS["playback_state"], headers=headers)

    if not res.ok or res.text == "":
        raise Exception(
            "Spotify get_playback_state request failed with a non-200 status code or no content was received."
        )

    return json.loads(res.text)


def get_currently_playing(access_token: str):
    """Get the currently playing track for a user.
    Docs: https://developer.spotify.com/documentation/web-api/reference/get-the-users-currently-playing-track

    Parameters
    ----------
    access_token: `str`
        User's bearer access token

    Returns
    -------
    `dict`
    """

    headers = {"Authorization": f"Bearer {access_token}"}

    res = requests.get(API_LINKS["currently_playing"], headers=headers)

    if not res.ok or res.text == "":
        raise Exception(
            "Spotify get_currently_playing request failed with a non-200 status code or no content was received."
        )

    return json.loads(res.text)


def get_playlist(access_token: str, playlist_id: str):
    """Get a playlist owned by a user.
    Docs: https://developer.spotify.com/documentation/web-api/reference/get-playlist

    Parameters
    ----------
    access_token: `str`
        User's bearer access token

    Returns
    -------
    `dict`
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    res = requests.get(API_LINKS["playlist"] + playlist_id, headers=headers)

    if not res.ok or res.text == "":
        raise Exception(
            "Spotify get_playlist request failed with a non-200 status code or no content was received."
        )

    return json.loads(res.text)
