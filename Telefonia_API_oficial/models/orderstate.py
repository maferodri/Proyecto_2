from pydantic import BaseModel, Field
from typing import Optional
import re

class OrderState(BaseModel): 
    id: Optional[str] = Field(
        default=None,
        description="ID generado por mongo"
    )
    