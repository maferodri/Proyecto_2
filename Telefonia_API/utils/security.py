import os 
import jwt

from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

SECRET_KEY = os.getenv("SECRETE_KEY") #tercera parte del token que manda firebase

#Funcion para crear un JWT
def create_jwt_token( #recibe los datos que se quiere codificar dentro del token 
        firstname:str
        , lastname:str
        , email:str
        , phone: str
        , active: bool
        , admin:bool
    ):
    expiration = datetime.utcnow() + timedelta(hours=1) #el token durara una hora
    token = jwt.encode( #crea el token, y los datos se codifican como el payload
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
    return token #devuelve el token

def validate_user(func): #una funcion para decorar que sea un usuario valido 
    @wraps(func) #mantiene el nombre y docstring de la función original
    async def wrapper( *args, **kwargs): #parametros de ejecucuión y acceder, acepta cualquier tipo de argumentos. args argumentos posicionales, kwargs argumentos con varibales 
        request = kwargs.get('request') #busca la clave request dentro del diccionario kwargs
        if not request: #si no la encuentra una excepcion   
            raise HTTPException(status_code = 400, detail= "Request object not found" ) 
        authorization: str = request.headers.get("Authorization") #busca el header authorizations osea el token
        if not authorization:
            raise HTTPException(status_code=400, detail="Authotization header missing")
        
        schema, token = authorization.split() #divide el tpken en schema 
        if schema.lower() != "bearer": #tiene que ser de tpo bearer
            raise HTTPException(status_code=400, detail="Invalid auth schema")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]) #
            
            #extrae datos importantes del payload del token 
            email = payload.get("email") #obtiene las variables
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