from bson import ObjectId

def get_inventory_type_pipeline() -> list:
    """
    Devuelve tipos de inventario con conteo de items
    """
    return [
        {"$addFields": {
            "id": {"$toString": "$_id"}
        }},
        {"$lookup": {
            "from": "Inventory",  # Nombre correcto en tu Mongo
            "localField": "id",
            "foreignField": "id_inventory_type",
            "as": "result"
        }},
        {"$addFields": {
            "number_of_items": {"$size": "$result"}  # Siempre presente, aunque sea 0
        }},
        {"$project": {
            "_id": 0,
            "id": 1,
            "description": 1,
            "active": 1,
            "number_of_items": 1
        }}
    ]

def validate_type_is_assigned_pipeline(id: str) -> list:
    """
    Valida si un tipo de inventario tiene items asignados
    """
    return [
        {"$match": {
            "_id": ObjectId(id)
        }},
        {"$addFields": {
            "id": {"$toString": "$_id"}
        }},
        {"$lookup": {
            "from": "Inventory",
            "localField": "id",
            "foreignField": "id_inventory_type",
            "as": "result"
        }},
        {"$addFields": {
            "number_of_items": {"$size": "$result"}
        }},
        {"$project": {
            "_id": 0,
            "id": 1,
            "description": 1,
            "active": 1,
            "number_of_items": 1
        }}
    ]
