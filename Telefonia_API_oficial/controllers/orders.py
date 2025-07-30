import logging

from bson import ObjectId
from models.orders import Order
from utils.mongodb import get_collection
from dotenv import load_dotenv
from fastapi import HTTPException
from pipelines.orders_pipeline import get_order_statistics_pipeline

logging.basicConfig(level= logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
coll= get_collection("Orders")
appointment_coll = get_collection("Appointments")
system_coll = get_collection("System")

async def create_order(order: Order) -> Order:
    try:
        appointment_exist = appointment_coll.find_one({"_id": ObjectId(order.appointment_id)})
        if  not appointment_exist:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        tax_result = system_coll.find_one({"key": "general_tax"})
        if tax_result and "value" in tax_result:
            try: 
                tax_rate = float(tax_result["value"])
            except ValueError:
                 raise HTTPException(status_code=500, detail="Tax rate must be numeric")    
        else:
            print("DEBUG: No se encontro tasa de impuesto")    
            tax_rate = 0.15
    
        order.subtotal = order.subtotal
        order.taxes = order.subtotal * tax_rate
        order.total = order.subtotal + order.taxes

        new_doc = order.model_dump(exclude={"id"})
        result = coll.insert_one(new_doc)
        order.id = str(result.inserted_id)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")
    
async def get_order_statistics():
    try:
        pipeline = get_order_statistics_pipeline()
        result = list(coll.aggregate(pipeline))
        return result[0] if result else {
            "total_orders": 0,
            "total_sales": 0.0,
            "avg_subtotal": 0.0,
            "total_taxes": 0.0,
            "max_order": 0.0,
            "min_order": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")    