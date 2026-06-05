from fastapi import FastAPI
from app.database import engine, Base
from app.models import schema
from app.api import analytics, customers, forecast, anomaly

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SalesPulse API",
    description="Real-Time Sales Analytics, Forecasting & Customer Intelligence Platform API",
    version="1.0.0"
)

app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
app.include_router(anomaly.router, prefix="/anomalies", tags=["Anomalies"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SalesPulse API"}
