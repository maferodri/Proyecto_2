import logging  
import uvicorn 

from fastapi import FastAPI
from dotenv import load_dotenv 

from routes.users import router as users_router
from routes.states import router as states_router
from routes.appointment import router as appointment_router
from routes.services import router as service_router
from routes.orders import router as orders_router

app = FastAPI()  

load_dotenv() 

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 

@app.get("/")  
def read_root():
    return {"Welcome to the app web of Telephony"}


app.include_router(users_router)
app.include_router(states_router)
app.include_router(appointment_router)
app.include_router(service_router)
app.include_router(orders_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")