from flask import Flask
from musicvision.spotify import SpotifyApp
from musicvision.env import getenv

# Set globally used SpotifyApp client
spotify_app = SpotifyApp(getenv("CLIENT_ID"), getenv("CLIENT_SECRET"))

# Import these submodules later, as they require spotify_app
from musicvision.general import general_bp
from musicvision.auth import auth_bp
from musicvision.api import api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=getenv("FLASK_SECRET_KEY"))

    app.register_blueprint(general_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    return app
