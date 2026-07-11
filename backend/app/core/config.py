import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is not set. "
        "The application cannot start without a secure secret key."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30