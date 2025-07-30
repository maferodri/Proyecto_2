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

load_dotenv()

cred = credentials.Certificate("secrets/telefonia-secreto.json") 
firebase_admin.initialize_app(cred) 

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
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
    payload = { 
        "email": user.email
        , "password": user.password
        , "returnSecureToken": True 
    }
    
    response = requests.post(url, json=payload) 
    response_data = response.json() 
    
    if "error" in response_data: 
        raise HTTPException( 
            status_code=400
            , detail= "Error in autenticating the user"
        )
    user_info = users_coll.find_one({ "email": user.email })  
    logger.info( user_info["name"]) #
    
    return { 
        "message": "Usuario Autenticado correctamente" 
        , "idToken": create_jwt_token( 
            user_info["name"]
            , user_info["lastname"]
            , user_info["email"]
            , user_info["phone"]
            , user_info["active"]
            , user_info["admin"]
        )
    }
        