from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.anomaly import detect

router = APIRouter()

@router.post("/detect")
def run_detection(db: Session = Depends(get_db)):
    detect.detect_anomalies(db)
    return {"message": "Anomaly detection completed"}

@router.get("/")
def get_anomalies(db: Session = Depends(get_db)):
    return detect.get_anomalies(db)
