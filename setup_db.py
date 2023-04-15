from musicvision.db import Base, db
from musicvision.env import getenv

DB_URI = getenv("DB_URI")

print(
    f"CAUTION: This will delete any previous records in database related to MusicVision at {DB_URI}.\nAre you sure you want to continue?"
)
input("Press Ctrl+C to cancel or any key to continue...")

Base.metadata.drop_all(db)
Base.metadata.create_all(db)
