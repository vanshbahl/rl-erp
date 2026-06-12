from fastapi import FastAPI

from app.core.database import Base, engine
from app.models import User

from app.routes.auth import router as auth_router
from app.routes.user import router as user_router
from app.routes import customer
from app.models.customer import Customer

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(customer.router)
Customer.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "RL ERP Backend Running"}