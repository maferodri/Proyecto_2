"""
Pipelines para InventoryTypes
"""
from bson import ObjectId


def get_inventory_type_pipeline(skip: int = 0, limit: int = 10) -> list:
    """
    Devuelve todos los tipos de inventario con el conteo de items en 'Inventory'
    """
    return [
        {
            "$lookup": {
                "from": "Inventory",
                "let": {"typeId": {"$toString": "$_id"}},
                "pipeline": [
                    {
                        "$addFields": {
                            "id_inventory_type_str": {
                                "$cond": [
                                    {"$eq": [{"$type": "$id_inventory_type"}, "objectId"]},
                                    {"$toString": "$id_inventory_type"},
                                    "$id_inventory_type"
                                ]
                            }
                        }
                    },
                    {
                        "$match": {
                            "$expr": {"$eq": ["$id_inventory_type_str", "$$typeId"]}
                        }
                    }
                ],
                "as": "items"
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "name": "$name",
                "active": "$active",
                "number_of_items": {"$size": "$items"}
            }
        },
        {"$skip": skip},
        {"$limit": limit}
    ]


def validate_type_is_assigned_pipeline(inventory_type_id: str) -> list:
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
