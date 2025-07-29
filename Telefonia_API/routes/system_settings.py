from fastapi import APIRouter, Request
from models.system_settings import SystemSetting
from utils.security import validate_admin

from controllers.system_settings import(
    create_system_settings
)

router = APIRouter()

@router.post("/systemsettings", response_model=SystemSetting, tags=["⚙️ System Settings"])
async def create_settings_endpoint(request: Request, system: SystemSetting) -> SystemSetting:
    return await create_system_settings(system)
