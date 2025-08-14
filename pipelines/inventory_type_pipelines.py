from bson import ObjectId

def get_inventory_type_pipeline() -> list:
    """
    Devuelve cada InventoryType con el conteo de ítems relacionados en la colección "Inventory".
    Soporta id_inventory_type guardado como ObjectId o string.
    """
    return [
        # id como string para mostrar
        {"$addFields": {"id": {"$toString": "$_id"}}},

        # Join con Inventory (nombre exacto de la colección)
        {
            "$lookup": {
                "from": "Inventory",
                "let": {"typeId": {"$toString": "$_id"}},
                "pipeline": [
                    # Normalizar id_inventory_type a string (soporta ObjectId o string)
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
                    # Mach con el _id del tipo (como string)
                    {
                        "$match": {
                            "$expr": {"$eq": ["$id_inventory_type_str", "$$typeId"]}
                        }
                    }
                ],
                "as": "items"
            }
        },

        # Armar salida (sin _id original, conteo con $size)
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                # por si usas name o description según el modelo
                "name": {"$ifNull": ["$name", "$description"]},
                "active": "$active",
                "number_of_items": {"$size": "$items"}
            }
        }
    ]


def validate_type_is_assigned_pipeline(inv_type_id: str) -> list:
    """
    Dado un id de InventoryType, devuelve un documento con:
      - id, name/description, active
      - number_of_items: cuántos items en "Inventory" lo usan
    Útil para decidir si se desactiva o se elimina definitivamente.
    """
    return [
        {"$match": {"_id": ObjectId(inv_type_id)}},
        {"$addFields": {"idStr": {"$toString": "$_id"}}},

        {
            "$lookup": {
                "from": "Inventory",
                "let": {"typeId": "$idStr"},
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
                    {"$match": {"$expr": {"$eq": ["$id_inventory_type_str", "$$typeId"]}}}
                ],
                "as": "items"
            }
        },

        {
            "$project": {
                "_id": 0,
                "id": "$idStr",
                "name": {"$ifNull": ["$name", "$description"]},
                "active": "$active",
                "number_of_items": {"$size": "$items"}
            }
        }
    ]
