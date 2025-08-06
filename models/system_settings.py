from pydantic import BaseModel, Field
from typing import Optional

class SystemSetting(BaseModel):
    id: Optional[str] = Field(
        default=None
        )          
    key: str = Field(
        description="Clave única de la configuración"
        )
    value: int = Field(..., 
        description="Valor numérico de la configuración"
        )
    description: Optional[str] = None       