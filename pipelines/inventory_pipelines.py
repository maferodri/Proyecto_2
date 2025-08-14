from bson import ObjectId

def validate_inventory_type_pipeline(inventory_type_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(inventory_type_id), "active": True}},
        {"$project": {"id": {"$toString": "$_id"}, "name": 1, "active": 1}}
    ]

def get_inventory_with_type_pipeline(inventory_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(inventory_id)}},
        {"$addFields": {"id_inventory_type_obj": {"$toObjectId": "$id_inventory_type"}}},
        {"$lookup": {
            "from": "inventorytypes",
            "localField": "id_inventory_type_obj",
            "foreignField": "_id",
            "as": "inventory_type"
        }},
        {"$unwind": "$inventory_type"},
        {"$project": {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "id_inventory_type": {"$toString": "$id_inventory_type"},
            "name": 1,
            "creation_date": 1,
            "active": 1,
            "inventory_type_name": "$inventory_type.name"
        }}
    ]

def get_all__with_types_pipeline(skip: int = 0, limit: int = 10) -> list:
    return [
        {"$addFields": {"id_inventory_type_obj": {"$toObjectId": "$id_inventory_type"}}},
        {"$lookup": {
            "from": "inventorytypes",
            "localField": "id_inventory_type_obj",
            "foreignField": "_id",
            "as": "inventory_type"
        }},
        {"$unwind": "$inventory_type"},
        {"$match": {"inventory_type.active": True}},  # opcional: sólo tipos activos
        {"$project": {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "id_inventory_type": {"$toString": "$id_inventory_type"},
            "name": 1,
            "creation_date": 1,
            "active": 1,
            "inventory_type_name": "$inventory_type.name"
        }},
        {"$skip": int(skip)},
        {"$limit": int(limit)}
    ]

def get_inventories_by_type_name_pipeline(type_name: str, skip: int = 0, limit: int = 10) -> list:
    return [
        {"$addFields": {"id_inventory_type_obj": {"$toObjectId": "$id_inventory_type"}}},
        {"$lookup": {
            "from": "inventorytypes",
            "localField": "id_inventory_type_obj",
            "foreignField": "_id",
            "as": "inventory_type"
        }},
        {"$unwind": "$inventory_type"},
        {"$match": {
            "inventory_type.name": {"$regex": f"^{type_name}$", "$options": "i"},
            "active": True
        }},
        {"$project": {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "id_inventory_type": {"$toString": "$id_inventory_type"},
            "name": 1,
            "creation_date": 1,
            "active": 1
        }},
        {"$skip": int(skip)},
        {"$limit": int(limit)}
    ]
