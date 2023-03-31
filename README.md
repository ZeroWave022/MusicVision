# MusicVision
A dashboard for everything about your music profile.
Currently supporting [Spotify](https://spotify.com/).

This project was made using [Flask](https://flask.palletsprojects.com/) in Python, and the database used is [PostgreSQL](https://www.postgresql.org/).

Note: This project is in its early stages of development.

# Installing

## Prerequisites
These must be installed before continuing with the installation.

- Python
- A PostgreSQL database
- A Spotify developer app

## Setting up the environment

- Clone the repository into a new folder
- Move to the newly created folder and set up a new virtual environment:

```
python3 -m venv venv
```

- [Activate](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) the virtual environment and install dependencies:
```
pip3 -r requirements.txt
```

## Setting up environmental variables
The app uses multiple secrets which should never be publicly available.
That's why a `.env` file is used for storing these.

A template follows below:

```
# Flask
FLASK_SECRET_KEY=""

# PostgreSQL Database URI with database name included (for example "musicvision")
DB_URI=""

# Spotify
CLIENT_ID=""
CLIENT_SECRET=""
REDIRECT_URI=""
SCOPE=""
```

Fill out missing fields in a `.env` which you place in the main folder (where `app.py` is).

## Preparing the database
Run `setup_db.py` to create the needed database which will be used.

## Running
MusicVision can now be run by executing `app.py` with Python.

# License
This project is licensed under the [Apache License 2.0](https://github.com/ZeroWave022/MusicVision/blob/main/LICENSE).

# Acknowledgements
This project or its author(s) are in no way associated with Spotify or any other streaming services.
The Spotify API is used in accordance with the [Spotify Developer Terms](https://developer.spotify.com/terms/).
