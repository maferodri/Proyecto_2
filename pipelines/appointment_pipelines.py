from datetime import datetime, timedelta
from bson import ObjectId

def date_appointment_pipeline(date_appointment: datetime, exclude_id: str = None) -> list:
    """
    Cuenta citas activas que caen en la ventana +/- 30 min para evitar solapes,
    excluyendo opcionalmente una cita por su ID.
    """
    match_stage = {
        "date_appointment": {
            "$gte": date_appointment - timedelta(minutes=30),
            "$lt": date_appointment + timedelta(minutes=30)
        },
        "active": True
    }

    if exclude_id and ObjectId.is_valid(exclude_id):
        match_stage["_id"] = {"$ne": ObjectId(exclude_id)}

    return [
        {"$match": match_stage},
        {"$count": "count"}
    ]

def get_user_appointments_pipeline(
    user_oid: ObjectId, skip: int = 0, limit: int = 10, include_inactive: bool = True
) -> list:
    # match por usuario (soporta user_id como ObjectId o string)
    match_user = {
        "$or": [
            {"user_id": user_oid},  # si está guardado como ObjectId
            {"$expr": {"$eq": [{"$toObjectId": "$user_id"}, user_oid]}}  # si es string
        ]
    }
    # si quisieras solo activas, cambia include_inactive=False
    if not include_inactive:
        match_user["active"] = True

    return [
        {"$match": match_user},

        # Para armar user_name en la salida:
        {"$addFields": {
            "user_id_obj": {
                "$cond": [
                    {"$eq": [{"$type": "$user_id"}, "objectId"]},
                    "$user_id",
                    {"$toObjectId": "$user_id"}
                ]
            }
        }},
        {"$lookup": {
            "from": "Users",        # OJO: cámbialo a "users" si tu colección es minúscula
            "localField": "user_id_obj",
            "foreignField": "_id",
            "as": "user_info"
        }},
        {"$unwind": "$user_info"},

        # ❌ NO FILTRAR user_info.active AQUÍ (para ver citas aunque el user esté inactivo)

        {"$sort": {"date_creation": -1}},
        {"$skip": int(skip)},
        {"$limit": int(limit)},

        {"$project": {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "user_id": {"$toString": "$user_id"},
            "date_appointment": 1,
            "date_creation": 1,
            "comment": "$comment",
            "active": "$active",
            "user_name": {
                "$let": {
                    "vars": {
                        "fullname": {
                            "$trim": {
                                "input": {
                                    "$concat": [
                                        {"$ifNull": ["$user_info.firstname", ""]},
                                        " ",
                                        {"$ifNull": ["$user_info.lastname", ""]}
                                    ]
                                }
                            }
                        }
                    },
                    "in": {
                        "$cond": [
                            {"$ifNull": ["$user_info.name", False]},
                            "$user_info.name",
                            "$$fullname"
                        ]
                    }
                }
            }
        }}
    ]


def get_all_appointments_pipeline(skip: int = 0, limit: int = 10) -> list:
    """
    Todas las citas (enriquecidas con el usuario). Por defecto filtra a usuarios activos.
    Incluye id y active de la CITA para que el front pinte bien el estado.
    """
    return [
        # Soporta user_id como ObjectId o como string
        {
            "$addFields": {
                "user_id_obj": {
                    "$cond": [
                        {"$eq": [{"$type": "$user_id"}, "objectId"]},
                        "$user_id",
                        {"$toObjectId": "$user_id"}
                    ]
                }
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
        {"$unwind": "$user_info"},
        # Si quieres ver citas aunque el usuario esté inactivo, comenta este $match
        {"$match": {"user_info.active": True}},

        {"$sort": {"date_creation": -1}},
        {"$skip": int(skip)},
        {"$limit": int(limit)},

        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},         # clave única para React
                "user_id": {"$toString": "$user_id"},
                "user_name": "$user_info.name",
                "date_appointment": 1,
                "date_creation": 1,
                "comment": "$comment",
                "active": "$active"                  # estado de la CITA (no del usuario)
            }
        }
    ]


def get_appointment_by_id_pipeline(appointment_id: str) -> list:
    """
    Cita por ID (enriquecida con usuario). Devuelve id y active de la cita.
    """
    return [
        {"$match": {"_id": ObjectId(appointment_id)}},
        {
            "$addFields": {
                "user_id_obj": {
                    "$cond": [
                        {"$eq": [{"$type": "$user_id"}, "objectId"]},
                        "$user_id",
                        {"$toObjectId": "$user_id"}
                    ]
                }
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
        {"$unwind": "$user_info"},
        # Si quieres ver la cita aunque el usuario esté inactivo, comenta este $match
        {"$match": {"user_info.active": True}},
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "user_name": "$user_info.name",
                "user_id": {"$toString": "$user_id"},
                "date_appointment": 1,
                "date_creation": 1,
                "comment": "$comment",
                "active": "$active"   # estado de la CITA
            }
        }
    ]


def validate_user_pipeline(user_id: str) -> list:
    """
    Valida que el usuario exista y esté activo.
    """
    return [
        {
            "$match": {
                "_id": ObjectId(user_id),
                "active": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "name": 1,
                "active": 1,
                "admin": 1
            }
        }
    ]
