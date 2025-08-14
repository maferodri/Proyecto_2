from models.inventory import Inventory
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime

from pipelines.inventory_pipelines import (
    validate_inventory_type_pipeline,
    get_inventory_with_type_pipeline,
    get_all_inventories_with_types_pipeline,
    get_inventories_by_type_name_pipeline
)

coll = get_collection("Inventory")
inventory_types_coll = get_collection("inventorytypes")

async def create_inventory(inventory: Inventory) -> Inventory:
    try:
        # Validar tipo
        type_pipe = validate_inventory_type_pipeline(inventory.id_inventory_type)
        type_result = list(inventory_types_coll.aggregate(type_pipe))
        if not type_result:
            raise HTTPException(status_code=400, detail="Inventory type not found or inactive")

        inventory.name = inventory.name.strip()
        # duplicado por nombre (case-insensitive)
        existing = coll.find_one({"name": {"$regex": f"^{inventory.name}$", "$options": "i"}})
        if existing:
            raise HTTPException(status_code=400, detail="Inventory item with this name already exists")

        inv_dict = inventory.model_dump(exclude={"id"})
        # Ajuste: la fecha de creación la asigna el servidor
        inv_dict["creation_date"] = datetime.utcnow()

        inserted = coll.insert_one(inv_dict)
        inventory.id = str(inserted.inserted_id)
        inventory.creation_date = inv_dict["creation_date"]
        return inventory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating inventory: {str(e)}")

async def get_inventories(skip: int = 0, limit: int = 1000) -> dict:
    try:
        pipeline = get_all_inventories_with_types_pipeline(skip, limit)
        items = list(coll.aggregate(pipeline))
        total = coll.count_documents({"active": True})
        return {"inventories": items, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching inventories: {str(e)}")

async def get_inventory_by_id(inventory_id: str) -> dict:
    try:
        pipeline = get_inventory_with_type_pipeline(inventory_id)
        result = list(coll.aggregate(pipeline))
        if not result:
            raise HTTPException(status_code=404, detail="Inventory not found")
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching inventory: {str(e)}")

async def get_inventories_by_type_name(type_name: str, skip: int = 0, limit: int = 10) -> dict:
    try:
        pipeline = get_inventories_by_type_name_pipeline(type_name, skip, limit)
        items = list(coll.aggregate(pipeline))

        # total para esa coincidencia
        count_pipe = [
            {"$addFields": {"id_inventory_type_obj": {"$toObjectId": "$id_inventory_type"}}},
            {"$lookup": {
                "from": "inventorytypes",
                "localField": "id_inventory_type_obj",
                "foreignField": "_id",
                "as": "inventory_type"
            }},
            {"$unwind": "$inventory_type"},
            {"$match": {
                "inventory_type.name": {"$regex": f"^{type_name}$", "$options": "i"},
                "active": True
            }},
            {"$count": "total"}
        ]
        count_res = list(coll.aggregate(count_pipe))
        total = count_res[0]["total"] if count_res else 0

        return {"inventories": items, "total": total, "skip": skip, "limit": limit, "type_name": type_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching inventories by type: {str(e)}")

async def update_inventory(inventory_id: str, inventory: Inventory) -> Inventory:
    try:
        # Validar tipo
        type_doc = inventory_types_coll.find_one({"_id": ObjectId(inventory.id_inventory_type)})
        if not type_doc:
            raise HTTPException(status_code=400, detail="Inventory type not found")

        inventory.name = inventory.name.strip()

        # nombre duplicado (excluyendo el propio id)
        exists = coll.find_one({
            "name": {"$regex": f"^{inventory.name}$", "$options": "i"},
            "_id": {"$ne": ObjectId(inventory_id)}
        })
        if exists:
            raise HTTPException(status_code=400, detail="Inventory item with this name already exists")

        res = coll.update_one(
            {"_id": ObjectId(inventory_id)},
            {"$set": inventory.model_dump(exclude={"id", "creation_date"})}  # no pisar creation_date
        )
        if res.modified_count == 0:
            raise HTTPException(status_code=404, detail="Inventory not found")

        return await get_inventory_by_id(inventory_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating inventory: {str(e)}")

async def deactivate_inventory(inventory_id: str) -> dict:
    try:
        res = coll.delete_one({"_id": ObjectId(inventory_id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Inventory not found")
        return {"message": "Inventory item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting inventory: {str(e)}")