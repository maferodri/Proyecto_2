import logging
from xmlrpc.client import _datetime

from bson import ObjectId
from models.appointment import Appointment
from utils.mongodb import get_collection
from fastapi import HTTPException, Request
from datetime import datetime, time, timedelta


from pipelines.appointment_pipelines import (
    date_appointment_pipeline,
    get_all_appointments_pipeline,
    get_appointment_by_id_pipeline,
    get_user_appointments_pipeline
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

coll= get_collection("Appointments")
users_coll = get_collection("Users")
settings_collection = get_collection("Services")


async def create_appointment_users(request: Request, appointment: Appointment) -> Appointment:
    try:
        # Validar rango horario permitido
        appointment_time = appointment.date_appointment.time()
        if not (time(9, 0) <= appointment_time <= time(17, 0)):
            raise HTTPException(status_code=400, detail="Appointments can only be created between 9:00 AM and 5:00 PM")

        # Obtener usuario autenticado desde el token
        email = request.state.email
        user_doc = users_coll.find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        is_admin = user_doc.get("admin", False)

        # VALIDACIÓN: Si es admin, debe mandar user_id
        if is_admin:
            if not appointment.user_id:
                raise HTTPException(status_code=400, detail="Admin must provide user_id to create an appointment")
            if not ObjectId.is_valid(appointment.user_id):
                raise HTTPException(status_code=400, detail="Invalid user_id format")
            user_obj_id = ObjectId(appointment.user_id)
        else:
            # Si no es admin, se asigna su propio ID (pero no puede crear para otros)
            if appointment.user_id and appointment.user_id != str(user_doc["_id"]):
                raise HTTPException(status_code=403, detail="Not authorized to create appointment for another user")
            user_obj_id = user_doc["_id"]

        # VALIDACIÓN 2: Evitar citas solapadas a nivel global
        pipeline = date_appointment_pipeline(appointment.date_appointment)
        result = list(coll.aggregate(pipeline))
        if result and result[0]["count"] > 0:
            raise HTTPException(status_code=400, detail="There is already an appointment scheduled at that time")

        # Preparar e insertar cita
        appointment_dict = appointment.model_dump(exclude={"id"})
        appointment_dict["user_id"] = user_obj_id
        appointment_dict["date_creation"] = datetime.utcnow()
        appointment_dict["active"] = True  # si usas campo active

        inserted = coll.insert_one(appointment_dict)

        # Preparar respuesta
        appointment.id = str(inserted.inserted_id)
        appointment.user_id = str(user_obj_id)
        appointment.date_creation = appointment_dict["date_creation"]

        return appointment

    except HTTPException:
        raise
    except Exception as e:
        result = list(coll.aggregate(pipeline))
        if result and result[0]["count"] > 0:
             raise HTTPException(status_code=400, detail="There is already an appointment scheduled at that time")
        # Insertar la cita
        appointment_dict = appointment.model_dump(exclude={"id"})
        appointment_dict["user_id"] = user_obj_id
        appointment_dict["date_creation"] = datetime.utcnow()

        inserted = coll.insert_one(appointment_dict)

        # Preparar respuesta
        appointment.id = str(inserted.inserted_id)
        appointment.user_id = str(user_obj_id)
        appointment.date_creation = appointment_dict["date_creation"]

        return appointment

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating appointment: {str(e)}")
    

async def get_appointments(current_user: dict, skip: int = 0, limit: int = 10) -> dict:
    """
    - Admin: devuelve todos los appointments.
    - Usuario normal: devuelve solo los suyos (user_id).
    """
    try:
        is_admin = bool(current_user.get("admin"))
        email = current_user.get("email")

        if is_admin:
            pipeline = get_all_appointments_pipeline(skip, limit)
            items = list(coll.aggregate(pipeline))
            total = coll.count_documents({"active": True})
        else:
            # Obtén el user_id desde tu colección users usando el email del token
            users = get_collection("users")
            user_doc = users.find_one({"email": email}, {"_id": 1})
            if not user_doc:
                # Por seguridad no revelamos si existe o no
                return {"appointments": [], "total": 0, "skip": skip, "limit": limit}

            user_oid = user_doc["_id"]  # ya es ObjectId
            pipeline = get_user_appointments_pipeline(user_oid, skip, limit)
            items = list(coll.aggregate(pipeline))
            total = coll.count_documents({"active": True, "user_id": user_oid})

        return {
            "appointments": items,
            "total": int(total),
            "skip": int(skip),
            "limit": int(limit),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving appointments: {str(e)}")

#CONTROLADOR PARA OPBTENER LA INFORMACIÓN DE UNA CITA EN ESPECIFICO PARA ADMINS
async def get_appointment_by_id(appointment_id: str) -> dict:
    try:
        pipeline = get_appointment_by_id_pipeline(appointment_id)
        result = list(coll.aggregate(pipeline))

        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")

        return result[0]  
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching appointment: {str(e)}")
    
    
async def update_appointment(appointment_id: str, appointment: Appointment, request:Request) -> Appointment:
        try:
            if not ObjectId.is_valid(appointment_id):
                raise HTTPException(status_code=400, detail="Invalid appointment ID format")

            existing = coll.find_one({"_id": ObjectId(appointment_id)})
            if not existing:
                raise HTTPException(status_code=404, detail="Appointment not found")
            
            # Validar que el usuario autenticado sea el dueño de la cita o admin
            user_doc = users_coll.find_one({"email": request.state.email})
            if not user_doc:
                 raise HTTPException(status_code=403, detail="User not found")

            is_owner = str(existing.get("user_id")) == str(user_doc["_id"])
            is_admin = user_doc.get("admin", False)

            if not (is_owner or is_admin):
                raise HTTPException(status_code=403, detail="Not authorized to modify this appointment")

            # Validar tiempo mínimo de 2 horas antes de la cita actual
            current_appointment_datetime = existing.get("date_appointment")
            if not isinstance(current_appointment_datetime, datetime):
                raise HTTPException(status_code=500, detail="Invalid date format stored in DB")
            
            #calcular lo de lad dos horas
            hours_result = settings_collection.find_one({"key": "hours_before_changes"})
            if hours_result and "value" in hours_result:
                hours_change = hours_result["value"]
            else: 
                print("DEBUG: No se encontro las horas que se pueden cambiar")    
                hours_change=24

            time_now = datetime.utcnow()
            if current_appointment_datetime - time_now < timedelta(hours=hours_change):
                raise HTTPException(
                    status_code=400,
                    detail="Appointments can only be updated at least 2 hours in advance"
                )
                
             # Validar que no haya citas solapadas (excluyendo la cita actual)
            pipeline = date_appointment_pipeline(appointment.date_appointment)
            conflicts = list(coll.aggregate(pipeline))
            if conflicts and conflicts[0]["count"] > 0:
                 raise HTTPException(status_code=400, detail="Another appointment already exists at that time")    

            # Validación y limpieza de comentario
            appointment.comment = appointment.comment.strip()

            result = coll.update_one(
                {"_id": ObjectId(appointment_id)},
                {"$set": appointment.model_dump(exclude={"id", "user_id"})}
            )

            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="No changes were made")

            # Obtener cita actualizada
            updated = coll.find_one({"_id": ObjectId(appointment_id)})
            updated["id"] = str(updated["_id"])
            updated["user_id"] = str(updated["user_id"])  # <-- ESTA LÍNEA es crucial
            return Appointment(**updated)


        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating appointment: {str(e)}")
        
async def disable_appointment(appointment_id: str,request:Request) -> dict:
        try:
            if not ObjectId.is_valid(appointment_id):
                raise HTTPException(status_code=400, detail="Invalid appointment ID format")
            
            existing = coll.find_one({"_id": ObjectId(appointment_id)})
            if not existing:
                raise HTTPException(status_code=404, detail="Appointment not found")
            
            # Validar que el usuario autenticado sea el dueño de la cita o admin
            user_doc = users_coll.find_one({"email": request.state.email})
            if not user_doc:
                raise HTTPException(status_code=403, detail="User not found")

            is_owner = str(existing.get("user_id")) == str(user_doc["_id"])
            is_admin = user_doc.get("admin", False)

            if not (is_owner or is_admin):
                raise HTTPException(status_code=403, detail="Not authorized to modify this appointment")


            # Validar tiempo mínimo de 2 horas antes de la cita
            appointment_datetime = existing.get("date_appointment")
            if not isinstance(appointment_datetime, datetime):
                raise HTTPException(status_code=500, detail="Invalid date format stored in DB")
            
            hours_result = settings_collection.find_one({"key": "hours_before_changes"})
            if hours_result and "value" in hours_result:
                hours_change = hours_result["value"]
            else: 
                print("DEBUG: No se encontro las horas que se pueden cambiar")    
                hours_change=2

            if appointment_datetime - datetime.utcnow() < timedelta(hours=hours_change):
                raise HTTPException(
                    status_code=400,
                    detail="Appointments can only be disabled at least 2 hours in advance"
                )

            result = coll.update_one(
                {"_id": ObjectId(appointment_id)},
                {"$set": {"active": False}}
            )

            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="No changes were made")

            return {"message": "Appointment successfully disabled"}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error disabling appointment: {str(e)}")    
                