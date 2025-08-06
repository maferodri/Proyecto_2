import logging
from typing import Optional

from bson import ObjectId
from models.service import Service
from utils.mongodb import get_collection
from dotenv import load_dotenv
from fastapi import HTTPException

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
        inserted = coll.insert_one(service_dict)
        service.id = str(inserted.inserted_id)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating service: {str(e)}")
    
async def get_services(filtro: Optional[str] = None) -> list[Service]:
    try:
        query = get_service_filter_pipeline(filtro)  

        services = []
        for doc in coll.find(query):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            services.append(Service(**doc))
        return services
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching services: {str(e)}")