from bson import ObjectId

def get_inventory_type_pipeline() -> list:
    return [
        {"$addFields": {"id": {"$toString": "$_id"}}},
        {"$lookup": {
            "from": "inventories",
            "localField": "id",
            "foreignField": "id_inventory_type",
            "as": "items"
        }},
        {"$group": {
            "_id": {"id": "$id", "name": "$name", "active": "$active"},
            "number_of_items": {"$sum": {"$size": "$items"}}
        }},
        {"$project": {
            "_id": 0,
            "id": "$_id.id",
            "name": "$_id.name",
            "active": "$_id.active",
            "number_of_items": 1
        }}
    ]

def validate_type_is_assigned_pipeline(id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(id)}},
        {"$addFields": {"id": {"$toString": "$_id"}}},
        {"$lookup": {
            "from": "inventories",
            "localField": "id",
            "foreignField": "id_inventory_type",
            "as": "items"
        }},
        {"$group": {
            "_id": {"id": "$id", "name": "$name", "active": "$active"},
            "number_of_items": {"$sum": {"$size": "$items"}}
        }},
        {"$project": {
            "_id": 0,
            "id": "$_id.id",
            "name": "$_id.name",
            "active": "$_id.active",
            "number_of_items": 1
        }}
    ]
