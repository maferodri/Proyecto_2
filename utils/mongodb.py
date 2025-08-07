import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

DB = os.getenv("DATABASE_NAME")
URI = os.getenv("MONGODB_URI")

if not DB:
    raise ValueError("Database name not found. Set DATABASE_NAME enviornment variable")
if not URI:
    raise ValueError("MongoDB URI not found. Set MONGODB_URI enviornment variable")

_client = None
def get_mongo_client():
    """"Obtiene el cliente de MongoDB (lazy loading)"""
    global _client
    if _client is None:
        _client = MongoClient(  
            URI
            , server_api = ServerApi("1")
            , tls = True
            , tlsAllowInvalidCertificates = True
            , serverSelectionTimeoutMS=5000
        )
    return _client    

def get_collection( col ):
    """"Obtiene una coleccion de MongoDB"""
    client = get_mongo_client()
    return client[DB][col]

def t_connection():
    """Funcion para probar la conexion (solo cuando sea necesario)"""
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return True
    except Exception as e: 
        print (f"Error connection to MongoDB: {e}")
        return False