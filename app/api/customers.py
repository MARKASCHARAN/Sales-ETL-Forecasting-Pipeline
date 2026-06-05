from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.customer_intelligence import rfm, churn

router = APIRouter()

@router.post("/calculate-rfm")
def calculate_rfm_segments(db: Session = Depends(get_db)):
    rfm.calculate_rfm(db)
    return {"message": "RFM segments calculated successfully"}

@router.get("/segments")
def get_segments(db: Session = Depends(get_db)):
    return rfm.get_segments(db)

@router.get("/churn-risk")
def get_churn_risk(db: Session = Depends(get_db)):
    return churn.predict_churn(db)

@router.get("/clv")
def get_clv(db: Session = Depends(get_db)):
    return churn.get_clv(db)
