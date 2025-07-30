import os
from fastapi import APIRouter, Body, HTTPException, Header, Path, Query, Request
from models.appointment import Appointment, StandardResponse
from utils.mongodb import get_collection
from utils.security import SECRET_KEY, validate_admin, validate_user
from firebase_admin import auth as firebase_auth  

from controllers.appointment import(
    create_appointment_users,
    get_appointments_admin,
    get_appointment_by_id,
    update_appointment,
    disable_appointment
)

router = APIRouter()

@router.post("/appointments", response_model=Appointment, tags=["🗓️ Appointments"])
@validate_user
async def create_appointment_endpoint(request:Request, appointment: Appointment) -> Appointment:
    return await create_appointment_users(request, appointment)


@router.get("/appointments", response_model=dict, tags=["🗓️ Appointments"])
@validate_admin
async def get_appointment_lookup_endpoint(request: Request) -> dict:
    return await get_appointments_admin()

@router.get("/appointments/{appointment_id}", response_model=dict, tags=["🗓️ Appointments"])
@validate_admin
async def get_appointment_by_id_endpoint(appointment_id:str ,request: Request) -> dict:
    return await get_appointment_by_id(appointment_id)


@router.put("/appointments/{appointment_id}", response_model=Appointment, tags=["🗓️ Appointments"])
@validate_user
async def update_appointment_route(appointment_id: str, appointment: Appointment,request: Request
):
    return await update_appointment(appointment_id, appointment, request)

@router.delete("/appointments/{appointment_id}", tags=["🗓️ Appointments"])
@validate_user
async def disable_appointment_endpoint(appointment_id: str, request: Request):
    return await disable_appointment(appointment_id, request)