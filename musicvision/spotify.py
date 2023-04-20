import requests
import json
from base64 import b64encode

API_LINKS = {
    "login": "https://accounts.spotify.com/authorize",
    "token": "https://accounts.spotify.com/api/token",
    "current_user": "https://api.spotify.com/v1/me",
    "artists": "https://api.spotify.com/v1/artists",
    "tracks": "https://api.spotify.com/v1/tracks",
    "playback_state": "https://api.spotify.com/v1/me/player",
    "currently_playing": "https://api.spotify.com/v1/me/player/currently-playing",
    "playlist": "https://api.spotify.com/v1/playlists/",
    "top": "https://api.spotify.com/v1/me/top/",
    "start_playback": "https://api.spotify.com/v1/me/player/play",
    "pause_playback": "https://api.spotify.com/v1/me/player/pause",
}


class SpotifyApp:
    """A client for interacting with the Spotify Web API.
    This class is to be used for interactions as a Spotify App.
    For interactions as a user, see the SpotifyUser class.
    """

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_links = API_LINKS

        self.session = requests.Session()
        self.session.headers = {
            "Authorization": f"Basic {self._b64_auth_header()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _b64_auth_header(self) -> str:
        auth = f"{self.client_id}:{self.client_secret}".encode()
        return b64encode(auth).decode()

    def gen_user_auth_link(self, redirect_uri: str, scope: str, state: str) -> str:
        """Create a Spotify link where a user can authenticate the app.

        Parameters
        ----------
        redirect_uri: str
            The redirect URI which will be used.
        scope: str
            The scope(s) which the app will used.
        state: str
            The generated state to use for this authentication.

        Returns
        -------
        `dict`
        """
        base_link = self.api_links["login"]
        return f"{base_link}?client_id={self.client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}&state={state}"

    def get_user_token(self, code: str, redirect_uri: str) -> dict:
        """Get a user's token after they have approved the app.

        Parameters
        ----------
        code: str
            The code returned from the API on the redirect URI upon authorization.
        redirect_uri:
            The same redirect URI which was used for the authorization step.

        Returns
        -------
        `dict`
        """
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }

        res = self.session.post(self.api_links["token"], params=params)

        if not res.ok or res.text == "":
            raise Exception(
                "Spotify get_user_token request failed with a non-200 status code or no content was received."
            )

        return json.loads(res.text)

    def refresh_token(self, old_token: str) -> dict:
        """Refresh a user's token.

        Parameters
        ----------
        old_token: str
            The refresh token for the user which needs a new access token.

        Returns
        -------
        `dict`
        """
        params = {"grant_type": "refresh_token", "refresh_token": old_token}

        res = self.session.post(self.api_links["token"], params=params)

        return json.loads(res.text)


class SpotifyUser:
    """A client for interacting with the Spotify API.
    This class is to be used for interactions as a user.
    For interactions as a Spotify App, see the SpotifyApp class.
    """

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.api_links = API_LINKS

        self.session = requests.Session()
        self.session.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _raise_failed_request(self, req_name: str) -> None:
        raise Exception(
            f"Spotify {req_name} request failed with a non-200 status code or no content was received."
        )

    def get_profile(self) -> dict:
        """Get this user's profile from the Spotify API.
        Docs: https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile

        Returns
        -------
        `dict`
        """
        res = self.session.get(self.api_links["current_user"])

        if not res.ok or res.text == "":
            self._raise_failed_request("get_profile")

        return json.loads(res.text)

    def get_artist(self, id: str) -> dict:
        """Get an artist.
        Docs: https://developer.spotify.com/documentation/web-api/reference/get-an-artist

        Returns
        -------
        `dict`
        """
        res = self.session.get(self.api_links["artists"] + f"/{id}")

        if not res.ok or res.text == "":
            self._raise_failed_request("get_artist")

        return json.loads(res.text)

    def get_artists(self, ids: list[str]) -> dict:
        """Get multiple artists.
        Docs: https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists

        Returns
        -------
        `dict`
        """
        ids_list = ",".join(ids)
        res = self.session.get(self.api_links["artists"], params={"ids": ids_list})

        if not res.ok or res.text == "":
            self._raise_failed_request("get_artists")

        return json.loads(res.text)

    def get_track(self, id: str) -> dict:
        """Get a track.
        Docs: https://developer.spotify.com/documentation/web-api/reference/get-track

        Returns
        -------
        `dict`
        """
        res = self.session.get(self.api_links["tracks"] + f"/{id}")

        if not res.ok or res.text == "":
            self._raise_failed_request("get_track")

        return json.loads(res.text)

    def get_tracks(self, ids: list[str]) -> dict:
        """Get multiple tracks.
        Docs: https://developer.spotify.com/documentation/web-api/reference/get-several-tracks

        Returns
        -------
        `dict`
        """
        ids_list = ",".join(ids)
        res = self.session.get(self.api_links["tracks"], params={"ids": ids_list})

        if not res.ok or res.text == "":
            self._raise_failed_request("get_tracks")

        return json.loads(res.text)

    def get_playback_state(self) -> dict:
        """Get playback state for this user.
        Docs: https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback

        Returns
        -------
        `dict`
        """
        res = self.session.get(self.api_links["playback_state"])

        if not res.ok or res.text == "":
            self._raise_failed_request("get_playback_state")

        return json.loads(res.text)

    def get_currently_playing(self) -> dict | bool:
        """Get the currently playing track for this user.
        Docs: https://developer.spotify.com/documentation/web-api/reference/get-the-users-currently-playing-track

        Returns
        -------
        `dict` if successful.
        Returns `False` if nothing is playing.
        """
        res = self.session.get(self.api_links["currently_playing"])

        if not res.ok or res.text == "":
            return False

        return json.loads(res.text)

    def get_playlist(self, playlist_id: str) -> dict:
        """Get a playlist owned by a user.
        Docs: https://developer.spotify.com/documentation/web-api/reference/get-playlist

        Parameters
        ----------
        playlist_id: `str`
            The Spotify ID of the playlist.

        Returns
        -------
        `dict`
        """
        res = self.session.get(self.api_links["playlist"] + playlist_id)

        if not res.ok or res.text == "":
            self._raise_failed_request("get_playlist")

        return json.loads(res.text)

    def get_top(
        self, item_type: str, time_range: str, limit: int = 20, offset: int = 0
    ) -> dict:
        """Get top artists or tracks for a user.
        Docs: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks

        Parameters
        ----------
        item_type: `str`
            Whether to get top artists or tracks.
            Possible values: `"artists"` or `"tracks"`.
        time_range: `str`
            The time frame which should be used to calculate artist popularities.
            Possible values: `"short_term"`, `"medium_term"` or `"long_term"`.
        limit: `str`
            The number of items.
        offset: `str`
            The index of the first item which will be returned.

        Returns
        -------
        `dict`
        """
        if item_type not in ["artists", "tracks"]:
            raise ValueError(
                'The `item_type` parameter must be one of the following: "artists" or "tracks".'
            )

        if time_range not in ["short_term", "medium_term", "long_term"]:
            raise ValueError(
                'The `time_frame` parameter must be one of the following: "short_term", "medium_term", "long_term".'
            )

        params = {"time_range": time_range, "limit": limit, "offset": offset}

        res = self.session.get(self.api_links["top"] + item_type, params=params)

        if not res.ok or res.text == "":
            self._raise_failed_request("get_top")

        return json.loads(res.text)

    def toggle_playback(self, toggle: bool) -> bool:
        """Toggle playback for a user.
        Docs (play): https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback
        Docs (pause): https://developer.spotify.com/documentation/web-api/reference/pause-a-users-playback

        Parameters
        ----------
        toggle: `bool`
            Whether to resume or pause playback for this user.
            `True` to resume, `False` to pause.

        Returns
        -------
        `bool`
            `True` if successful, `False` if failed.
        """
        if toggle:
            res = self.session.put(self.api_links["start_playback"])
        else:
            res = self.session.put(self.api_links["pause_playback"])

        if res.status_code != 204:
            return False

        return True
