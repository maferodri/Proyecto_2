from typing import Optional
from fastapi import APIRouter, Query, Request
from models.service import Service
from utils.security import validate_admin

from controllers.service import(
    create_service,
    get_services,
    get_service_by_id,
    update_service,
    deactivate_service
)

router = APIRouter()

@router.post("/services", response_model=Service, tags=["🛠️ Service"])
@validate_admin
async def create_service_endpoint(request: Request, service: Service) -> Service:
    return await create_service(service)

@router.get("/services", response_model=list[Service], tags=["🛠️ Service"])
async def get_services_querystring_endpoint(
    request: Request,
    filtro: Optional[str] = Query(default=None, description="Buscar por nombre o descripción"),
    include_inactive: bool = Query(default=False, description="Incluir servicios inactivos")
) -> list[Service]:
    return await get_services(filtro, include_inactive)

@router.get("/services/{service_id}", response_model=Service, tags=["🛠️ Service"])
async def get_service_by_id_endpoint(request: Request, service_id: str) -> Service:
    return await get_service_by_id(service_id)

@router.put("/services/{service_id}", response_model=Service, tags=["🛠️ Service"])
@validate_admin
async def update_service_endpoint(request: Request, service_id: str, service: Service) -> Service:
    return await update_service(service_id, service, request)

@router.delete("/services/{service_id}", response_model=dict, tags=["🛠️ Service"])
@validate_admin
async def deactivate_service_endpoint(request: Request, service_id: str) -> dict:
    return await deactivate_service(service_id, request)