import psycopg
import psycopg.sql
import os
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI")
DB_NAME = os.getenv("DB_NAME").lower()

print(
    f"CAUTION: This will delete any previous records in the {DB_NAME} database at {DB_URI}.\nAre you sure you want to continue?"
)
input("Press Ctrl+C to cancel or any key to continue...")

with psycopg.connect(DB_URI) as conn:
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database")

        all_dbs = cur.fetchall()
        db_names = [elem[0] for elem in all_dbs]

        if DB_NAME in db_names:
            cur.execute(psycopg.sql.SQL("DROP DATABASE {}".format(DB_NAME)))

        cur.execute(psycopg.sql.SQL("CREATE DATABASE {}".format(DB_NAME)))

with psycopg.connect(f"{DB_URI}/{DB_NAME}") as conn:
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
