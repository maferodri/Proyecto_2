from models.inventorytypes import InventoryType
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId

from pipelines.inventory_type_pipelines import (
    get_inventory_type_pipeline,
    validate_type_is_assigned_pipeline
)

coll = get_collection("inventorytypes")

async def create_inventory_type(inv_type: InventoryType) -> InventoryType:
    try:
        inv_type.name = inv_type.name.strip().lower()
        existing = coll.find_one({"name": inv_type.name})
        if existing:
            raise HTTPException(status_code=400, detail="Inventory type already exists")

        doc = inv_type.model_dump(exclude={"id"})
        inserted = coll.insert_one(doc)
        inv_type.id = str(inserted.inserted_id)
        return inv_type
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating inventory type: {str(e)}")

async def get_inventory_types() -> list:
    try:
        pipeline = get_inventory_type_pipeline()
        return list(coll.aggregate(pipeline))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching inventory types: {str(e)}")

async def get_inventory_type_by_id(inv_type_id: str) -> InventoryType:
    try:
        doc = coll.find_one({"_id": ObjectId(inv_type_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Inventory type not found")
        doc["id"] = str(doc["_id"]); del doc["_id"]
        return InventoryType(**doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching inventory type: {str(e)}")

async def update_inventory_type(inv_type_id: str, inv_type: InventoryType) -> InventoryType:
    try:
        inv_type.name = inv_type.name.strip().lower()
        existing = coll.find_one({"name": inv_type.name, "_id": {"$ne": ObjectId(inv_type_id)}})
        if existing:
            raise HTTPException(status_code=400, detail="Inventory type already exists")

        res = coll.update_one(
            {"_id": ObjectId(inv_type_id)},
            {"$set": inv_type.model_dump(exclude={"id"})}
        )
        if res.modified_count == 0:
            raise HTTPException(status_code=404, detail="Inventory type not found")

        return await get_inventory_type_by_id(inv_type_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating inventory type: {str(e)}")

async def deactivate_inventory_type(inv_type_id: str) -> dict:
    try:
        pipeline = validate_type_is_assigned_pipeline(inv_type_id)
        assigned = list(coll.aggregate(pipeline))
        if assigned is None:
            raise HTTPException(status_code=404, detail="Inventory type not found")

        if assigned and assigned[0]["number_of_items"] > 0:
            coll.update_one({"_id": ObjectId(inv_type_id)}, {"$set": {"active": False}})
            return {"message": "Inventory type is assigned to items and has been deactivated"}
        else:
            coll.delete_one({"_id": ObjectId(inv_type_id)})
            return {"message": "Inventory type deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating inventory type: {str(e)}")
