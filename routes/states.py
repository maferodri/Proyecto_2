from fastapi import APIRouter, Request
from models.states import State
from utils.security import validate_admin

from controllers.states import(
    create_state,
    get_states,
    get_state_id,
    update_state,
    desactivate_state
)

router = APIRouter()

@router.post("/states", response_model=State, tags=["⏳ States"])
@validate_admin
async def create_state_endpoint(request: Request, state: State) -> State:
    return await create_state(state)

@router.get("/states", response_model=list[State], tags=["⏳ States"])
@validate_admin
async def get_states_endpoints(request:Request) -> list[State]:
    return await get_states()

@router.get("/states/{state_id}", response_model=State, tags=["⏳ States"])
@validate_admin
async def get_state_id_endpoint(request: Request, state_id: str) -> State:
    return await get_state_id(state_id)

@router.put("/states/{state_id}", response_model=State, tags=["⏳ States"])
@validate_admin
async def update_state_endpoint(request: Request, state_id: str, state: State) -> State:
    return await update_state(state_id, state)   

@router.delete("/states/{state_id}", response_model=State, tags=["⏳ States"])
@validate_admin
async def desactivate_state_endpoint(request: Request, state_id: str) -> State:
    return await desactivate_state(state_id)
  