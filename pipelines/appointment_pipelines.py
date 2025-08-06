from bson import ObjectId
from datetime import timedelta, datetime

def date_appointment_pipeline(date_appointment: datetime) -> list:
    return [
        {
            "$match": {
                "date_appointment": {
                    "$gte": date_appointment - timedelta(minutes=30),
                    "$lt": date_appointment + timedelta(minutes=30)
                },
                "active": True  # ← si estás usando citas activas
            }
        },
        {"$count": "count"}
    ]

def get_user_appointments_pipeline(user_object_id):
    return [
        {"$match": {"user_id": user_object_id}},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "user_id": {"$toString": "$user_id"}
        }},
        {"$project": {"_id": 0}}  # quitamos el _id original
    ]


def get_all_appointments_pipeline(skip: int = 0, limit: int = 10) -> list:
    """
    Pipeline para obtener todos los catálogos con información del tipo
    """
    return [
  {
    "$addFields": {
      "user_id_obj": {"$toObjectId": "$user_id"}
    }
  },
  {
    "$lookup": {
      "from": "Users",
      "localField": "user_id_obj",
      "foreignField": "_id",
      "as": "user_info"
    }
  },
  {
    "$unwind": "$user_info"
  },
  {
    "$match": {
      "user_info.active": True
    }
  },
  {
    "$project": {
      "_id": 0
      , "user_name": "$user_info.name"
      , "user_id": { "$toString": "$user_id" }
      , "date_appointment": "$date_appointment"
      , "creaation_date": "$date_creation"
      , "comments": "$comment"
    }
  }
]
    
def get_appointment_by_id_pipeline(appointment_id: str) -> list:
    """
    Pipeline para obtener una cita por su ID con información del usuario (sin mostrar _id ni user_id)
    """
    return [
        {
            "$match": {
                "_id": ObjectId(appointment_id)
            }
        },
        {
            "$addFields": {
                "user_id_obj": {"$toObjectId": "$user_id"}
            }
        },
        {
            "$lookup": {
                "from": "Users",
                "localField": "user_id_obj",
                "foreignField": "_id",
                "as": "user_info"
            }
        },
        {
            "$unwind": "$user_info"
        },
        {
            "$match": {
                "user_info.active": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "user_name": "$user_info.name",
                "user_id": { "$toString": "$user_id" },
                "date_appointment": "$date_appointment",
                "creaation_date": "$date_creation",
                "comment": "$comment"
            }
        }
    ]
         
#pipeline para saber si un usuario esta         
def validate_user_pipeline(user_id: str) -> list: 
    return [
        {"$match": {
            "_id": ObjectId(user_id),
            "active": True
        }},
        {"$project": {
            "id": {"$toString": "$_id"},
            "description": 1,
            "active": 1,
            "admin": 1
        }}
    ]