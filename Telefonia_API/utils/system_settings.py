from models.system_settings import SystemSetting
from utils.mongodb import get_collection

async def get_system_setting(key: str) -> SystemSetting:
    collection = get_collection("System Settings")
    doc = await collection.find_one({"key": key})
    if not doc:
        raise Exception(f"Setting '{key}' no encontrado")
    return SystemSetting(**doc)
