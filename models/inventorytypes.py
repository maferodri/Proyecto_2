from  pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class InventoryType(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB, no es necesario enviarlo en POST"
    )

    name: str = Field(
        description="Descripción del tipo de catálogo",
        pattern=r"^[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
        examples=["Product","Bundle"]
    )

    active: Optional[bool] = Field(
        default=True,
        description="Estado activo del tipo de catálogo"
    )