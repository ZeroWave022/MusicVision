from musicvision.db import User, db
from musicvision.env import getenv

DB_URI = getenv("DB_URI")

print(
    f"CAUTION: This will delete any previous records in the {User.__name__} database at {DB_URI}.\nAre you sure you want to continue?"
)
input("Press Ctrl+C to cancel or any key to continue...")


db.drop_tables([User])
db.create_tables([User])

db.commit()
db.close()
