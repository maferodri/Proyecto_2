import re
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Inventory(BaseModel):
    id: Optional[str] = Field(default=None, description="MongoDB ID")

    id_inventory_type: str = Field(
        description="FK to InventoryType (_id as string)", 
        examples=["507f1f77bcf86cd799439011"]
    )

    name: str = Field(
        description="Inventory item name",
        pattern = r"^[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
        examples=["iPhone 14 Pro", "Laptop XPS 13"]
    )

    # 👇 ÚNICO ajuste pedido: fecha de creación se setea sola
    creation_date: Optional[datetime] = Field(
        default=None,
        description="Creation datetime; server sets it on create"
    )

    active: bool = Field(default=True, description="Is the inventory item active?")
