import os
from dotenv import load_dotenv

load_dotenv("../.env")

def getenv(var: str):
    return os.getenv(var)
