import logging  
import uvicorn 

from fastapi import FastAPI
from dotenv import load_dotenv 

from routes.users import router as users_router
from routes.states import router as states_router
from routes.appointment import router as appointment_router
from routes.services import router as service_router
from routes.orders import router as orders_router
from routes.inventory import router as inventory_router
from routes.inventorytypes import router as inventorytypes_router

app = FastAPI()  

#Add CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"], 
)

load_dotenv() 

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 


@app.get("/")  
def read_root():
    return {"status": "healthy", "version": "0.0.0", "service": "telefonia-api"}

@app.get("/health")
def health_check():
    try:
        return{
            "status": "healthy",
            "timestamp": "2025-08-06",
            "service": "telefonia-api",
            "environment": "production"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}    
    
@app.get("/ready")
def readiness_check():
    try:
        from utils.mongodb import test_connection
        db_status = test_connection()
        return {
            "status": "ready" if db_status else "not_ready",
            "database": "connected" if db_status else "disconnected",
            "service": "telefonia-api"
        }
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}        


app.include_router(users_router)
app.include_router(states_router)
app.include_router(appointment_router)
app.include_router(service_router)
app.include_router(orders_router)
app.include_router(inventory_router)
app.include_router(inventorytypes_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")