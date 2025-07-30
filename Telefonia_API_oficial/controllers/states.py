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
        state.name = state.name.strip().lower() 
        existing_type = coll.find_one({"name": state.name}) 
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
        state = [] 
        
        for doc in coll.find(): 
            doc['id'] = str(doc['_id']) 
            del doc['_id'] 
            state_obj = State(**doc) 
            state.append(state_obj) 
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching state: {str(e)}")
    
    
async def get_state_id(state_id: str) ->State: 
    try:
        doc = coll.find_one({"_id": ObjectId(state_id)}) 
        if not doc: 
            raise HTTPException(status_code=404, detail="State not found")

        doc['id'] = str(doc['_id'])
        del doc['_id']
        return State(**doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching state: {str(e)}")


async def update_state(state_id: str, state: State) -> State:
    try:
        state.name = state.name.strip().lower()
        existing_type = coll.find_one({"name": state.name,"_id": {"$ne": ObjectId(state_id)}}) 
        if existing_type:
            raise HTTPException(status_code=400, detail="State name already exists")
        
        state_dict = state.model_dump(exclude={"id"})

        result = coll.update_one( 
            {"_id": ObjectId(state_id)},
            {"$set": state_dict} 
        )

        if result.matched_count == 0: 
            raise HTTPException(status_code=404, detail="State not found")
        state.id = state_id
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating state: {str(e)}")
    
async def desactivate_state(state_id: str) -> State:
    try:
        result = coll.update_one(
            {"_id": ObjectId(state_id)},
            {"$set": {"active": False}} 
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="State not found")

        return await get_state_id(state_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating state: {str(e)}")   
