import peewee
from musicvision.env import getenv
from urllib.parse import urlparse

DB_URI = getenv("DB_URI")
parsed = urlparse(DB_URI)

db = peewee.PostgresqlDatabase(
    "musicvision",
    host=parsed.hostname,
    port=parsed.port,
    user=parsed.username,
    password=parsed.password,
)


class User(peewee.Model):
    id = peewee.TextField(primary_key=True)
    access_token = peewee.TextField()
    token_type = peewee.TextField()
    scope = peewee.TextField()
    refresh_token = peewee.TextField()
    expires_at = peewee.BigIntegerField()

    class Meta:
        database = db


db.connect()
