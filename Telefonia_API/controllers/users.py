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

logging.basicConfig(level=logging.INFO) #Hay varios mensajes tipo logging. y cada uno tiene un nivel numero, entonces el level muestra de ese nivel para arriba
logger = logging.getLogger(__name__) #Esto crea un logger con el nombre del archivo actual.

load_dotenv()

cred = credentials.Certificate("secrets/telefonia-secreto.json") #credenciales para conectarse con firebase
firebase_admin.initialize_app(cred) #con las credenciales iniciamos nuestro servicio de Firebase

users_coll = get_collection("Users") 

async def create_user(user : User)  -> User: #el user sera de tipo User
    user_record = {} #crea un diccionario vacio. Aquí guardaremos la creación del usuario de FireBase
    
    try: #este primer try nos sirve para crear el usuario
        user_record = firebase_auth.create_user( #crea un nuevo usuario en FireBase, que devuelve un objeto de tipo UserRecord
            email=user.email, #usa el correo
            password=user.password #usa la contraseña
        )
    except Exception as e:
        logger.warning(e)    #se registra en los logs como advertencia 
        raise HTTPException( #cancela totalmente la ejecución 
             status_code=400 #damos el codigo del error
            ,detail="Error in registrating user in FireBase"
        )
    
    try:
        user_dict = user.model_dump(exclude={"id", "password"}) #construir diccionario para hacerlo como json usando model_dumb y se excluye el id y la ocntra
        inserted = users_coll.insert_one( user_dict) #inserta el diccionario que creamos arriba en la colección de mongo
        user.id = str(inserted.inserted_id) #convierte el id generado por mongo a un string
        return user #nos retorna el objeto usuario
    except Exception as e: #este error es por si algo falla al conectarse con mongo
        firebase_auth.delete_user( user_record.uid ) #se borra el usuario creado en firebase
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    
async def login(user: Login) -> dict: #recibe un parametro user que es tipo Login y retorna un diccionario
    api_key = os.getenv("FIREBASE_API_KEY") #obtiene el api_key para hacer el login
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
    payload = { #esto es lo que se le envia a firebase, las credenciales del usuario
        "email": user.email
        , "password": user.password
        , "returnSecureToken": True 
    }
    
    response = requests.post(url, json=payload) #envia una solicitud POST a firebase con los datos 
    response_data = response.json() #convierte la respuesta a json
    
    if "error" in response_data: #si la linea error esta en la respuesta del json que nos mando firebase
        raise HTTPException( #mandamos una excepcion
            status_code=400
            , detail= "Error in autenticating the user"
        )
    user_info = users_coll.find_one({ "email": user.email })  #busca al usuario por su email 
    logger.info( user_info["name"]) #imprime en los logs el nombre del usuario
    
    return { #retorna el token 
        "message": "Usuario Autenticado correctamente" 
        , "idToken": create_jwt_token( #creamos el JWT que incluye la infor del usuario
            user_info["name"]
            , user_info["lastname"]
            , user_info["email"]
            , user_info["phone"]
            , user_info["active"]
            , user_info["admin"]
        )
    }
        