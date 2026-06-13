from fastapi import FastAPI

from app.core.database import Base, engine

import app.models

from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.user import router as user_router
from app.routes import customer
from app.routes import product
from app.routes import inventory

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(customer.router)
app.include_router(product.router)
app.include_router(inventory.router)

@app.get("/")
def root():
    return {"message": "RL ERP Backend Running"}