import base64
import json
import os 
import logging 
import requests 
import firebase_admin 

from fastapi import HTTPException 
from dotenv import load_dotenv
from firebase_admin import credentials, auth as firebase_auth  

from models.users import User
from models.login import Login

from utils.security import create_jwt_token 
from utils.mongodb import get_collection

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 

def initialize_firebase():
    if firebase_admin._apps:
        return
    try:
        firebase_creds_base64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")
        if firebase_creds_base64:
            firebase_creds_json = base64.b64decode(firebase_creds_base64).decode('utf-8')
            firebase_creds = json.loads(firebase_creds_json)
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with environment variable credentials")
        else:
            cred = credentials.Certificate("secrets/telefonia-secreto.json")
            firebase_admin.initialize_app(cred)    
            logger.info("Firebase initialized with JSON file")
            
    except Exception as e:
        logger.error(f"Failed to initialized Firebase: {e}")
        raise HTTPException(status_code=500, detail=f"Firebase configuration error: {str(e)}")        

initialize_firebase()

users_coll = get_collection("Users") 

async def create_user(user : User)  -> User: 
    user_record = {} 
    
    try: 
        user_record = firebase_auth.create_user( 
            email=user.email, 
            password=user.password 
        )
    except Exception as e:
        logger.warning(e)    
        raise HTTPException( 
             status_code=400 
            ,detail="Error in registrating user in FireBase"
        )
    
    try:
        user_dict = user.model_dump(exclude={"id", "password"}) 
        inserted = users_coll.insert_one( user_dict) 
        user.id = str(inserted.inserted_id) 
        return user 
    except Exception as e: 
        firebase_auth.delete_user( user_record.uid ) 
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    
async def login(user: Login) -> dict:
    api_key = os.getenv("FIREBASE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Config de autenticación incompleta")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }

    try:
        resp = requests.post(url, json=payload, timeout=8)  # requests es sync; OK si lo aceptas
    except requests.RequestException:
        # Error de red/timeout con Firebase
        raise HTTPException(status_code=502, detail="Error de conexión con el proveedor de auth")

    data = resp.json() if resp.content else {}

    # Si Firebase responde error
    if resp.status_code != 200 or "error" in data:
        code = data.get("error", {}).get("message", "")
        # Mapa de errores más comunes de Firebase
        if code in ("EMAIL_NOT_FOUND", "INVALID_PASSWORD"):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        if code == "USER_DISABLED":
            raise HTTPException(status_code=403, detail="Usuario deshabilitado")
        # Otros errores (p.ej. TOO_MANY_ATTEMPTS_TRY_LATER, OPERATION_NOT_ALLOWED, etc.)
        raise HTTPException(status_code=502, detail="Error al iniciar sesión. Intenta más tarde.")

    # Buscar usuario en tu base (puede no existir aunque Firebase haya autenticado)
    user_info = users_coll.find_one({"email": user.email})
    if not user_info:
        # Decide si esto es 404 o 401; aquí 401 para no filtrar existencia
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_jwt_token(
        user_info.get("name"),
        user_info.get("lastname"),
        user_info.get("email"),
        user_info.get("phone"),
        user_info.get("active"),
        user_info.get("admin"),
    )

    return {
        "message": "Usuario autenticado correctamente",
        "token": token,
    }