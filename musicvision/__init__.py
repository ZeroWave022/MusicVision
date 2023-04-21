import logging
from flask import Flask
from musicvision.spotify import SpotifyApp
from musicvision.env import getenv

# Set globally used SpotifyApp client
spotify_app = SpotifyApp(getenv("CLIENT_ID"), getenv("CLIENT_SECRET"))

# Import these modules later, as some of them require spotify_app
from musicvision.general import general_bp
from musicvision.dashboard import dashboard_bp
from musicvision.auth import auth_bp
from musicvision.api import api_bp
from musicvision.legal import legal_bp
from musicvision.tasks import start_tasks

# Set up logging when package is initialized
logging.basicConfig(
    format="[%(levelname)s] [%(asctime)s] [%(module)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=getenv("FLASK_SECRET_KEY"))

    app.register_blueprint(general_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(legal_bp)

    start_tasks()

    return app
