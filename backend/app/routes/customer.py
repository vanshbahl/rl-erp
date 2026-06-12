from fastapi import APIRouter

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

@router.get("/")
def get_customers():
    return {"message": "Customer route working"}