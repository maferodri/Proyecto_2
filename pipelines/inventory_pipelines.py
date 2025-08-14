"""
Pipelines para Inventory
"""
from bson import ObjectId


def validate_inventory_type_pipeline(inventory_type_id: str) -> list:
    """
    Valida que un tipo de inventario exista y esté activo
    """
    return [
        {
            "$match": {
                "_id": ObjectId(inventory_type_id),
                "active": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "name": "$name",
                "active": "$active"
            }
        }
    ]


def get_inventory_with_type_pipeline(inventory_id: str) -> list:
    """
    Devuelve un inventario específico con información de su tipo
    """
    return [
        {"$match": {"_id": ObjectId(inventory_id)}},
        {
            "$addFields": {
                "id_inventory_type_obj": {
                    "$cond": [
                        {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                        "$id_inventory_type",
                        {"$toObjectId": "$id_inventory_type"}
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "inventorytypes",
                "localField": "id_inventory_type_obj",
                "foreignField": "_id",
                "as": "inventory_type"
            }
        },
        {"$unwind": "$inventory_type"},
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "id_inventory_type": {"$toString": "$id_inventory_type_obj"},
                "name": "$name",
                "active": "$active",
                "creation_date": "$creation_date",
                "inventory_type_name": "$inventory_type.name"
            }
        }
    ]


def get_all_inventories_with_types_pipeline(skip: int = 0, limit: int = 10) -> list:
    """
    Devuelve todos los inventarios con información de su tipo
    """
    return [
        {
            "$addFields": {
                "id_inventory_type_obj": {
                    "$cond": [
                        {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                        "$id_inventory_type",
                        {"$toObjectId": "$id_inventory_type"}
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "inventorytypes",
                "localField": "id_inventory_type_obj",
                "foreignField": "_id",
                "as": "inventory_type"
            }
        },
        {"$unwind": "$inventory_type"},
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "id_inventory_type": {"$toString": "$id_inventory_type_obj"},
                "name": "$name",
                "active": "$active",
                "creation_date": "$creation_date",
                "inventory_type_name": "$inventory_type.name"
            }
        },
        {"$skip": skip},
        {"$limit": limit}
    ]


def get_inventories_by_type_name_pipeline(type_name: str, skip: int = 0, limit: int = 10) -> list:
    """
    Devuelve inventarios filtrados por el nombre de su tipo
    """
    return [
        {
            "$addFields": {
                "id_inventory_type_obj": {
                    "$cond": [
                        {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                        "$id_inventory_type",
                        {"$toObjectId": "$id_inventory_type"}
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "inventorytypes",
                "localField": "id_inventory_type_obj",
                "foreignField": "_id",
                "as": "inventory_type"
            }
        },
        {"$unwind": "$inventory_type"},
        {
            "$match": {
                "inventory_type.name": {"$regex": f"^{type_name}$", "$options": "i"},
                "active": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "id_inventory_type": {"$toString": "$id_inventory_type_obj"},
                "name": "$name",
                "active": "$active",
                "creation_date": "$creation_date",
                "inventory_type_name": "$inventory_type.name"
            }
        },
        {"$skip": skip},
        {"$limit": limit}
    ]
