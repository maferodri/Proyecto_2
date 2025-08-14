from bson import ObjectId

def get_inventory_with_type_pipeline(inventory_id: str) -> list:
    """
    Pipeline para obtener un inventario con información de su tipo
    """
    return [
        {"$match": {"_id": ObjectId(inventory_id)}},
        {"$addFields": {
            "id_inventory_type_obj": {"$toObjectId": "$id_inventory_type"}
        }},
        {"$lookup": {
            "from": "inventorytypes",
            "localField": "id_inventory_type_obj",
            "foreignField": "_id",
            "as": "inventory_type"
        }},
        {"$unwind": "$inventory_type"},
        {"$project": {
            "id": {"$toString": "$_id"},
            "id_inventory_type": {"$toString": "$id_inventory_type"},
            "name": "$name",
            "description": "$description",
            "active": "$active",
            "inventory_type_description": "$inventory_type.description"
        }}
    ]

def get_inventories_by_type_name_pipeline(type_description: str, skip: int = 0, limit: int = 10) -> list:
    """
    Pipeline para obtener inventarios filtrados por tipo
    """
    return [
        {"$addFields": {
            "id_inventory_type_obj": {"$toObjectId": "$id_inventory_type"}
        }},
        {"$lookup": {
            "from": "inventorytypes",
            "localField": "id_inventory_type_obj",
            "foreignField": "_id",
            "as": "inventory_type"
        }},
        {"$unwind": "$inventory_type"},
        {"$match": {
            "inventory_type.description": {"$regex": f"^{type_description}$", "$options": "i"},
            "active": True
        }},
        {"$project": {
            "id": {"$toString": "$_id"},
            "id_inventory_type": {"$toString": "$id_inventory_type"},
            "name": "$name",
            "description": "$description",
            "active": "$active"
        }},
        {"$skip": skip},
        {"$limit": limit}
    ]

def get_all_inventories_with_types_pipeline(skip: int = 0, limit: int = 10) -> list:
    """
    Pipeline para obtener todos los inventarios con información del tipo
    """
    return [
        {"$addFields": {
            "id_inventory_type_obj": {"$toObjectId": "$id_inventory_type"}
        }},
        {"$lookup": {
            "from": "inventorytypes",
            "localField": "id_inventory_type_obj",
            "foreignField": "_id",
            "as": "inventory_type"
        }},
        {"$unwind": "$inventory_type"},
        {"$match": {
            "inventory_type.active": True
        }},
        {"$project": {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "id_inventory_type": {"$toString": "$id_inventory_type"},
            "name": "$name",
            "description": "$description",
            "active": "$active",
            "inventory_type_description": "$inventory_type.description"
        }},
        {"$skip": skip},
        {"$limit": limit}
    ]

def validate_inventory_type_pipeline(inventory_type_id: str) -> list:
    """
    Pipeline para validar que un inventory type existe y está activo
    """
    return [
        {"$match": {
            "_id": ObjectId(inventory_type_id),
            "active": True
        }},
        {"$project": {
            "id": {"$toString": "$_id"},
            "description": "$description",
            "active": "$active"
        }}
    ]
