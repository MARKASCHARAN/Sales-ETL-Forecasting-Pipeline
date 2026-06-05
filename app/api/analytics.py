from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.analytics import kpi

router = APIRouter()

@router.get("/revenue")
def get_revenue(db: Session = Depends(get_db)):
    return {"total_revenue": kpi.get_total_revenue(db)}

@router.get("/profit-margin")
def get_profit_margin(db: Session = Depends(get_db)):
    return {"profit_margin": kpi.get_profit_margin(db)}

@router.get("/top-products")
def get_top_products(limit: int = 5, db: Session = Depends(get_db)):
    return {"top_products": kpi.get_top_products(db, limit)}

@router.get("/monthly-revenue")
def get_monthly_revenue(db: Session = Depends(get_db)):
    return {"monthly_revenue": kpi.get_monthly_revenue(db)}
