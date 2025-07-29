from fastapi import HTTPException
from utils.system_settings import get_system_setting
from utils.mongodb import get_collection
from models.system_settings import SystemSetting

coll = get_collection("System Settings")

async def create_system_settings(system: SystemSetting) -> SystemSetting:
    try:
        system_dict = system.model_dump(exclude={"id"})
        existing = coll.find_one({"key": system.key})
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe una configuración con esa clave")

        result = coll.insert_one(system_dict)
        system.id = str(result.inserted_id)
        return system
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear configuración: {str(e)}")


async def get_system_setting(key: str) -> SystemSetting:
    try:
        doc = coll.find_one({"key": key})
        if not doc:
            raise Exception(f"Configuración '{key}' no encontrada")
        doc["id"] = str(doc["_id"])
        return SystemSetting(**doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener configuración: {str(e)}")