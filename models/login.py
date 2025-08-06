import re
from pydantic import BaseModel, Field, field_validator

class Login(BaseModel):

    email: str = Field( 
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", #ayuda a validar sobre los que son permitidos
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
    