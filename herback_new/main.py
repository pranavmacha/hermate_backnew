import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.symptom_model import SymptomPayload
from agent.agent import generate_symptom_advice
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HerMate AI Backend", version="1.0.0")

# Configure CORS with specific origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

@app.get("/")
def home():
    return {"message": "HerMate AI Backend Running"}

@app.post("/ai/symptom-advice")
def symptom_advice(payload: SymptomPayload):
    """Generate AI-powered symptom advice based on user input.
    
    Args:
        payload (SymptomPayload): User symptom data
        
    Returns:
        dict: Advice response with structured recommendations
    """
    logger.info(f"Symptom advice requested: severity={payload.severity}, cycle_day={payload.cycle_day}")
    advice = generate_symptom_advice(payload.dict())
    return {"advice": advice}
