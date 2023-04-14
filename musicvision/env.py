import os
from dotenv import load_dotenv

load_dotenv()


def getenv(var: str):
    return os.getenv(var)
