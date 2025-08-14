from fastapi import APIRouter, Request
from models.inventorytypes import InventoryType
from controllers.inventorytypes import (
    create_inventory_type,
    get_inventory_types,
    get_inventory_type_by_id,
    update_inventory_type,
    deactivate_inventory_type
)
from utils.security import validate_user, validate_admin

router = APIRouter(tags=["🏷️ Inventory Types"])

@router.post("/inventorytypes", response_model=InventoryType)
@validate_user
async def create_inventory_type_endpoint(request: Request, inv_type: InventoryType) -> InventoryType:
    return await create_inventory_type(inv_type)

@router.get("/inventorytypes", response_model=list)
@validate_user
async def get_inventory_types_endpoint(request: Request) -> list:
    return await get_inventory_types()

@router.get("/inventorytypes/{inv_type_id}", response_model=InventoryType)
@validate_user
async def get_inventory_type_by_id_endpoint(request: Request, inv_type_id: str) -> InventoryType:
    return await get_inventory_type_by_id(inv_type_id)

@router.put("/inventorytypes/{inv_type_id}", response_model=InventoryType)
@validate_user
async def update_inventory_type_endpoint(request: Request, inv_type_id: str, inv_type: InventoryType) -> InventoryType:
    return await update_inventory_type(inv_type_id, inv_type)

@router.delete("/inventorytypes/{inv_type_id}", response_model=dict)
@validate_user
async def deactivate_inventory_type_endpoint(request: Request, inv_type_id: str) -> dict:
    return await deactivate_inventory_type(inv_type_id)
