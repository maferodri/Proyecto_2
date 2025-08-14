from fastapi import APIRouter, Request
from models.inventory import Inventory
from controllers.inventory import (
    create_inventory,
    get_inventories,
    get_inventory_by_id,
    update_inventory,
    deactivate_inventory
)
from utils.security import validate_user, validate_admin  

router = APIRouter(tags=["📦 Inventories"])

@router.post("/inventories", response_model=Inventory)
@validate_user
async def create_inventory_endpoint(request: Request, inventory: Inventory) -> Inventory:
    return await create_inventory(inventory)

@router.get("/inventories", response_model=dict)
async def get_inventories_endpoint(skip: int = 0, limit: int = 1000) -> dict:
    return await get_inventories(skip, limit)

@router.get("/inventories/{inventory_id}", response_model=dict)
async def get_inventory_by_id_endpoint(inventory_id: str) -> dict:
    return await get_inventory_by_id(inventory_id)

@router.put("/inventories/{inventory_id}", response_model=dict)
@validate_user
async def update_inventory_endpoint(request: Request, inventory_id: str, inventory: Inventory) -> dict:
    return await update_inventory(inventory_id, inventory)

@router.delete("/inventories/{inventory_id}", response_model=dict)
@validate_user
async def deactivate_inventory_endpoint(request: Request, inventory_id: str) -> dict:
    return await deactivate_inventory(inventory_id)
