from typing import Optional

def get_service_filter_pipeline(filtro: Optional[str] = None) -> dict:
    query = {}

    if filtro:
        query["$or"] = [
            {"name": {"$regex": filtro, "$options": "i"}},
            {"description": {"$regex": filtro, "$options": "i"}}
        ]
    
    return query