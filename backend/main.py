from fastapi import FastAPI

from app.core.database import Base

import app.models

from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.user import router as user_router
from app.routes import customer
from app.routes import product
from app.routes import inventory
from app.routes import order
from app.routes import invoice
from app.routes import payment
from app.routes import supplier
from app.routes import purchase_order
from app.routes.bom import router as bom_router
from app.routes.production_order import router as production_order_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(customer.router)
app.include_router(product.router)
app.include_router(inventory.router)
app.include_router(order.router)
app.include_router(invoice.router)
app.include_router(payment.router)
app.include_router(supplier.router)
app.include_router(purchase_order.router)
app.include_router(bom_router)
app.include_router(production_order_router)

@app.get("/Health")
def root():
    return {"message": "TESTED: OK"}