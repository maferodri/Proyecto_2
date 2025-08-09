import os 
import jwt

from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") 

def create_jwt_token( 
        firstname:str
        , lastname:str
        , email:str
        , phone: str
        , active: bool
        , admin:bool
    ):
    expiration = datetime.utcnow() + timedelta(hours=1) 
    token = jwt.encode( 
        {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "phone": phone, 
            "active": active,
            "admin": admin, 
            "exp": expiration,
            "iat": datetime.utcnow()
        },
        SECRET_KEY,
        algorithm= "HS256"
    )
    return token 

def validate_user(func):  
    @wraps(func) 
    async def wrapper( *args, **kwargs): 
        request = kwargs.get('request') 
        if not request:   
            raise HTTPException(status_code = 400, detail= "Request object not found" ) 
        authorization: str = request.headers.get("Authorization") 
        if not authorization:
            raise HTTPException(status_code=400, detail="Authotization header missing")
        
        schema, token = authorization.split() 
        if schema.lower() != "bearer": 
            raise HTTPException(status_code=400, detail="Invalid auth schema")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]) #
            
            email = payload.get("email") 
            firstname = payload.get("firstname")
            lastname = payload.get("lastname")
            phone = payload.get("phone")
            active= payload.get("active")
            exp = payload.get("exp")
            admin = payload.get("admin")
            
            #validación de campos
            if email is None:
                raise HTTPException(status_code=401, detail="Token invalid")
            
            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Expired token")
            
            if not active:
                raise HTTPException(status_code=401, detail="Inactive user")
            
            #guarda info en request.state
            request.state.email = email
            request.state.firstname = firstname
            request.state.lastname = lastname
            request.state.phone = phone
            request.state.admin = admin
            
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token or expired token")    

        
        return await func( *args, **kwargs) #retorna la función original
    
    return wrapper  #devuelve la función decorada


def validate_admin(func):
    @wraps(func)
    async def wrapper( *args, **kwargs): #parametros de ejecucuión y acceder
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code = 400, detail= "Request objecto not found" )
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authotization header missing")
        
        schema, token = authorization.split()
        if schema.lower() != "bearer": 
            raise HTTPException(status_code=400, detail="Invalid auth schema")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            email = payload.get("email")
            firstname = payload.get("firstname")
            lastname = payload.get("lastname")
            admin= payload.get("admin")
            active=payload.get("active")
            exp = payload.get("exp")
            
            if email is None:
                raise HTTPException(status_code=401, detail="Token invalid")
            
            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Expired token")
            
            if not active or not admin:
                raise HTTPException(status_code=401, detail="Inactive user or not admin")
            
            request.state.email = email
            request.state.firstname = firstname
            request.state.lastname = lastname
            request.state.admin = admin
            
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token or expired token")    
        
        return await func( *args, **kwargs)
    
    return wrapper 