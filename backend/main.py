from fastapi import FastAPI

from app.core.database import Base, engine
from app.models import User

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "RL ERP Backend Running"
    }