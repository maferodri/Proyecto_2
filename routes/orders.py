from fastapi import APIRouter, Request
from models.orders import Order
from utils.security import validate_admin

from controllers.orders import(
    create_order,
    get_order_statistics
)

router = APIRouter()

@router.post("/orders", response_model=Order, tags=["📦 Orders"])
@validate_admin
async def create_order_endpoint(request: Request, order: Order) -> Order:
    return await create_order(order)

@router.get("/statistics", tags=["📊 Estadísticas"])
@validate_admin
async def get_order_statistics_endpoints(request: Request):
    return await get_order_statistics()

