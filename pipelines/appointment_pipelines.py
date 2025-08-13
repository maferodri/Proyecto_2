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

def get_user_appointments_pipeline(user_oid: ObjectId, skip: int = 0, limit: int = 10) -> list:
    """
    Solo citas del usuario (soporta user_id guardado como ObjectId o como string).
    Incluye active=True, orden por date_creation desc, paginación y esquema homogéneo.
    """
    return [
        # match por user_id ya sea ObjectId o string convertible
        {
            "$match": {
                "active": True,
                "$or": [
                    {"user_id": user_oid},  # si está guardado como ObjectId
                    {
                        "$expr": {
                            "$eq": [
                                {"$toObjectId": "$user_id"},  # si está como string
                                user_oid
                            ]
                        }
                    }
                ]
            }
        },
        {"$sort": {"date_creation": -1}},
        {"$skip": int(skip)},
        {"$limit": int(limit)},
        {
            "$addFields": {
                "id": {"$toString": "$_id"},
                "user_id": {
                    "$cond": [
                        {"$eq": [{"$type": "$user_id"}, "objectId"]},
                        {"$toString": "$user_id"},
                        "$user_id"
                    ]
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "date_appointment": 1,
                "date_creation": 1,
                "comments": "$comment"
            }
        }
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