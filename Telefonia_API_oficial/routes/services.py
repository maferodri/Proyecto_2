from typing import Optional
from fastapi import APIRouter, Query, Request
from models.service import Service
from utils.security import validate_admin

from controllers.service import(
    create_service,
    get_services
)

router = APIRouter()

@router.post("/services", response_model=Service, tags=["🛠️ Service"])
@validate_admin
async def create_service_endpoint(request: Request, service: Service) -> Service:
    return await create_service(service)

@router.get("/services", response_model=list[Service], tags=["🛠️ Service"])
async def get_services_querystring_endpoint(
    request: Request,
    filtro: Optional[str] = Query(default=None, description="Buscar por nombre o descripción")
) -> list[Service]:
    return await get_services(filtro)