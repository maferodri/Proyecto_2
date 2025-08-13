import logging
from typing import Optional

from bson import ObjectId
from models.service import Service
from utils.mongodb import get_collection
from dotenv import load_dotenv
from fastapi import HTTPException, Request

from pipelines.service_pipelines import get_service_filter_pipeline

logging.basicConfig(level= logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
coll= get_collection("Services")

async def create_service(service: Service) -> Service:
    try:
        service.name = service.name.strip().lower() 
        existing_type = coll.find_one({"name": service.name})  
        if existing_type:
            raise HTTPException(status_code=400, detail="Service already exists")
        

        service_dict = service.model_dump(exclude={"id"})
        if "active" not in service_dict:
            service_dict["active"] = True; 
        
        inserted = coll.insert_one(service_dict)
        service.id = str(inserted.inserted_id)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating service: {str(e)}")
    
async def get_services(filtro: Optional[str] = None) -> list[Service]:
    try:
        query = get_service_filter_pipeline(filtro)  
        query["active"] = True

        services = []
        for doc in coll.find(query):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            services.append(Service(**doc))
        return services
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching services: {str(e)}")
    
async def get_service_by_id(service_id: str) -> Service:
    try:
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service ID format")

        doc = coll.find_one({"_id": ObjectId(service_id), "active": True})
        if not doc:
            raise HTTPException(status_code=404, detail="Service not found")

        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Service(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching service: {str(e)}")

async def update_service(service_id: str, service: Service, request: Request) -> Service:
    try:
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service ID format")

        existing = coll.find_one({"_id": ObjectId(service_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Service not found")

        # normalizar nombre y evitar duplicados (excluyendo el propio id)
        new_name = service.name.strip().lower()
        dup = coll.find_one({"name": new_name, "_id": {"$ne": ObjectId(service_id)}})
        if dup:
            raise HTTPException(status_code=400, detail="Service already exists")

        update_doc = service.model_dump(exclude={"id"})
        update_doc["name"] = new_name  # mantener normalizado

        res = coll.update_one({"_id": ObjectId(service_id)}, {"$set": update_doc})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        if res.modified_count == 0:
            # nada cambió, pero devolvemos el recurso actual
            updated = coll.find_one({"_id": ObjectId(service_id)})
        else:
            updated = coll.find_one({"_id": ObjectId(service_id)})

        updated["id"] = str(updated["_id"])
        del updated["_id"]
        return Service(**updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating service: {str(e)}")


async def deactivate_service(service_id: str, request: Request) -> dict:
    try:
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service ID format")

        existing = coll.find_one({"_id": ObjectId(service_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Service not found")

        res = coll.update_one({"_id": ObjectId(service_id)}, {"$set": {"active": False}})
        if res.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes were made")

        return {"message": "Service successfully deactivated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating service: {str(e)}")        