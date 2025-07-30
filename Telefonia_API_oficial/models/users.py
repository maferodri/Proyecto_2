import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional 

class User(BaseModel):
    
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID"
    )
    
    name: str = Field(  
        description="User First Name",
        pattern=r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
    ) 
    
    lastname: str = Field(
        description="User Last Name",
        pattern=r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
    )
    
    email: str = Field(
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", 
    )
    
    phone: str = Field(
        description="Users number phone",
        pattern=r"^(\+504\s?|504\s?|\(504\)\s?)?(\d{4})[- ]?(\d{4})$",
    )
    
    active: bool = Field(
        default=True 
    )
    
    admin: bool = Field(
        default=False
    )
    
    password: str = Field(
        min_length=8,
        max_length=64,
        description="Contraseña del usuario debe tener "
    )
    
    @field_validator('password') 
    @classmethod
    def validate_password_complexity(cls, value: str):
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe contener al menos un número.")
        if not re.search(r"[@$!%*?&]", value):
            raise ValueError("La contraseña debe contener al menos un carácter especial (@$!%*?&).")
        return value
    