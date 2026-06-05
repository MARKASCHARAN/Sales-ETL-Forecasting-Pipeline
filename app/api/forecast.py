from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.forecasting import predict

router = APIRouter()

@router.post("/generate")
def generate_forecast(db: Session = Depends(get_db)):
    predict.generate_forecast(db)
    return {"message": "Forecast generated successfully"}

@router.get("/")
def get_forecast(db: Session = Depends(get_db)):
    return predict.get_forecast(db)
