import os
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

def get_db_connection():
    DB_URI = os.getenv("DB_URI")
    DB_NAME = os.getenv("DB_NAME").lower()
    return connect(f"{DB_URI}/{DB_NAME}", row_factory=dict_row)

def query_db(query: str, params: list = None) -> None:
    """Insert, update, delete or perform any other action on the PostgreSQL database which doesn't require any returned values from the database.
    
    Parameters
    ----------
    query: `str`
        The SQL query with optional formatting parameters already in place.
    params: `Optional[list]`
        Optonal parameters which will be provided to the query.
    
    Returns
    -------
    `None`
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)

        conn.commit()

def fetch_db(query: str,  fetch_type: str | list, params: list = None):
    """Fetch one, many, or all items from the PostgreSQL database.
    
    Parameters
    ----------
    query: `str`
        The SQL query with optional formatting parameters already in place.
    fetch_type: `str` | `list`
        The type of fetch operation. Must be `"one"`, `"all"` or `["many", size]` (size indicates how many to fetch).
    params: `Optional[list]`
        Optonal parameters which will be provided to the query.
    
    Returns
    -------
    dict
        The fetched result.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            
            if isinstance(fetch_type, list) and fetch_type[0] == "many":
                res = cur.fetchmany(fetch_type[1])
            elif fetch_type == "one":
                res = cur.fetchone()
            elif fetch_type == "all":
                res = cur.fetchall()
            else:
                raise ValueError('The "fetch_type" must "one", "all" or ["many", size].')
    
    return res
