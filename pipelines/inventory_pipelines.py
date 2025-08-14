# pipelines/inventory_pipelines.py
from bson import ObjectId

def get_inventory_with_type_pipeline(inventory_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(inventory_id)}},
        {
            "$addFields": {
                "id_inventory_type_obj": {
                    "$cond": [
                        {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                        "$id_inventory_type",
                        {"$toObjectId": "$id_inventory_type"},
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "inventorytypes",   # <- minúscula
                "localField": "id_inventory_type_obj",
                "foreignField": "_id",
                "as": "inv_type"
            }
        },
        {"$unwind": {"path": "$inv_type", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "id_inventory_type": {
                    "$cond": [
                        {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                        {"$toString": "$id_inventory_type"},
                        "$id_inventory_type",
                    ]
                },
                "name": 1,
                "creation_date": 1,
                "active": 1,
                "inventory_type_name": {"$ifNull": ["$inv_type.name", "$inv_type.description"]},
            }
        }
    ]


def get_inventories_by_type_pipeline(inventory_type_name: str, skip: int = 0, limit: int = 10) -> list:
    return [
        {
            "$addFields": {
                "id_inventory_type_obj": {
                    "$cond": [
                        {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                        "$id_inventory_type",
                        {"$toObjectId": "$id_inventory_type"},
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "inventorytypes",   # <- minúscula
                "localField": "id_inventory_type_obj",
                "foreignField": "_id",
                "as": "inv_type"
            }
        },
        {"$unwind": {"path": "$inv_type", "preserveNullAndEmptyArrays": False}},
        {
            "$match": {
                "inv_type.name": {"$regex": f"^{inventory_type_name}$", "$options": "i"},
                "active": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "id_inventory_type": {
                    "$cond": [
                        {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                        {"$toString": "$id_inventory_type"},
                        "$id_inventory_type",
                    ]
                },
                "name": 1,
                "creation_date": 1,
                "active": 1,
                "inventory_type_name": {"$ifNull": ["$inv_type.name", "$inv_type.description"]},
            }
        },
        {"$skip": int(skip)},
        {"$limit": int(limit)},
    ]


def get_all_inventories_with_types_pipeline(skip: int = 0, limit: int = 10) -> list:
    return [
        {
            "$addFields": {
                "id_inventory_type_obj": {
                    "$cond": [
                        {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                        "$id_inventory_type",
                        {"$toObjectId": "$id_inventory_type"},
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "inventorytypes",   # <- minúscula
                "localField": "id_inventory_type_obj",
                "foreignField": "_id",
                "as": "inv_type"
            }
        },
        {"$unwind": {"path": "$inv_type", "preserveNullAndEmptyArrays": True}},
        {"$match": {"inv_type.active": True}},
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "id_inventory_type": {
                    "$cond": [
                        {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                        {"$toString": "$id_inventory_type"},
                        "$id_inventory_type",
                    ]
                },
                "name": 1,
                "creation_date": 1,
                "active": 1,
                "inventory_type_name": {"$ifNull": ["$inv_type.name", "$inv_type.description"]},
            }
        },
        {"$skip": int(skip)},
        {"$limit": int(limit)},
    ]


def validate_inventory_type_pipeline(inventory_type_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(inventory_type_id), "active": True}},
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "name": 1,
                "active": 1
            }
        }
    ]
