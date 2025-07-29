import logging

from bson import ObjectId
from models.states import State
from utils.mongodb import get_collection
from dotenv import load_dotenv
from fastapi import HTTPException

logging.basicConfig(level= logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
coll= get_collection("States")

async def create_state(state: State) -> State:
    try:
        state.name = state.name.strip().lower() #para que independiente del nombre lo haga minuscula
        existing_type = coll.find_one({"name": state.name}) #si el 
        if existing_type:
            raise HTTPException(status_code=400, detail="State already exists")

        state_dict = state.model_dump(exclude={"id"})
        inserted = coll.insert_one(state_dict)
        state.id = str(inserted.inserted_id)
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating state: {str(e)}")
    
    
async def get_states() -> list[State]:
    try:
        state = [] #lista vacia en general
        
        for doc in coll.find(): #devuelve todos los elementos de la coleccion gracias al for 
            doc['id'] = str(doc['_id']) #convierte el ObjectId de mongo _id lo convierte a un string de tipo id ya que es lo que espera el modelo
            del doc['_id'] #elimina el campo _id
            state_obj = State(**doc) # Se crea una instancia del modelo state usando **doc.
            state.append(state_obj) #agrega el state_obj al final de la lista
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching state: {str(e)}")
    
    
async def get_state_id(state_id: str) ->State: #usa la misma logica pero solo devuelve un objeta
    try:
        doc = coll.find_one({"_id": ObjectId(state_id)}) #creamos una instancia del documento usando el _id unico
        if not doc: #si el doc no esta: 
            raise HTTPException(status_code=404, detail="State not found")

        doc['id'] = str(doc['_id'])
        del doc['_id']
        return State(**doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching state: {str(e)}")


async def update_state(state_id: str, state: State) -> State:
    try:
        state.name = state.name.strip().lower()
        existing_type = coll.find_one({"name": state.name,"_id": {"$ne": ObjectId(state_id)}}) #Busca si ya existe otro estado con ese nombre, pero excluyendo el que estás editanedo
        if existing_type:
            raise HTTPException(status_code=400, detail="State name already exists")
        
        state_dict = state.model_dump(exclude={"id"})

        result = coll.update_one( #actualiza el documento
            {"_id": ObjectId(state_id)},
            {"$set": state_dict} #sobre escribe los campos que mande 
        )

        if result.matched_count == 0: #si no se encuentr ningun estado con ese ID entonces nos da un error
            raise HTTPException(status_code=404, detail="State not found")
        state.id = state_id
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating state: {str(e)}")
    
async def desactivate_state(state_id: str) -> State:
    try:
        result = coll.update_one(
            {"_id": ObjectId(state_id)},
            {"$set": {"active": False}} #solo cobreescribe el estado
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="State not found")

        return await get_state_id(state_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating state: {str(e)}")   
