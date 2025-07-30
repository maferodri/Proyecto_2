
def get_order_statistics_pipeline():
    return [
        {
            "$group": {
                "_id": None,
                "total_orders": {"$sum": 1},
                "total_sales": {"$sum": "$total"},
                "avg_subtotal": {"$avg": "$subtotal"},
                "total_taxes": {"$sum": "$taxes"},
                "max_order": {"$max": "$total"},
                "min_order": {"$min": "$total"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_orders": 1,
                "total_sales": 1,
                "avg_subtotal": 1,
                "total_taxes": 1,
                "max_order": 1,
                "min_order": 1
            }
        }
    ]