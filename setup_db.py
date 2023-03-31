import psycopg
import psycopg.sql
import os
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI")

splitted = DB_URI.split("/")
db_name = splitted[-1]
if "?" in splitted[-1]:
    index = db_name.index("?")
    db_name = db_name[:index]

print(
    f"CAUTION: This will delete any previous records in the {db_name} database at {DB_URI}.\nAre you sure you want to continue?"
)
input("Press Ctrl+C to cancel or any key to continue...")

with psycopg.connect(DB_URI, dbname="postgres") as conn:
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database")

        all_dbs = cur.fetchall()
        db_names = [elem[0] for elem in all_dbs]

        if db_name in db_names:
            cur.execute(psycopg.sql.SQL("DROP DATABASE {}".format(db_name)))

        cur.execute(psycopg.sql.SQL("CREATE DATABASE {}".format(db_name)))

with psycopg.connect(f"{DB_URI}") as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE users (
                id text PRIMARY KEY,
                access_token text,
                token_type text,
                scope text,
                refresh_token text,
                expires_at bigint
            )
            """
        )

    conn.commit()
