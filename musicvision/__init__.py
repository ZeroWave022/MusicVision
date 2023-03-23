from flask import Flask
from musicvision.general import general_bp
from musicvision.auth import auth_bp
from musicvision.env import getenv

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=getenv("FLASK_SECRET_KEY")
    )

    app.register_blueprint(general_bp)
    app.register_blueprint(auth_bp)

    return app
