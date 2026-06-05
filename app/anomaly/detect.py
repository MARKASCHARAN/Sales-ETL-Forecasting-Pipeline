import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.models.schema import Order, Anomaly
from datetime import datetime

def detect_anomalies(db: Session):
    orders = db.query(Order.order_date, Order.total_amount).all()
    if not orders:
        return []

    df = pd.DataFrame([(o.order_date, o.total_amount) for o in orders], columns=['order_date', 'total_amount'])
    df['order_date'] = pd.to_datetime(df['order_date']).dt.date
    daily_sales = df.groupby('order_date')['total_amount'].sum().reset_index()
    
    # Calculate Z-score
    mean = daily_sales['total_amount'].mean()
    std = daily_sales['total_amount'].std()
    
    daily_sales['z_score'] = (daily_sales['total_amount'] - mean) / std
    
    # Threshold for anomaly (e.g. Z > 2 or Z < -2)
    anomalies_df = daily_sales[np.abs(daily_sales['z_score']) > 2].copy()
    
    for _, row in anomalies_df.iterrows():
        # check if already saved
        existing = db.query(Anomaly).filter(Anomaly.date == row['order_date']).first()
        if not existing:
            anomaly_type = "Spike" if row['z_score'] > 0 else "Drop"
            severity = "High" if np.abs(row['z_score']) > 3 else "Medium"
            
            anom = Anomaly(
                anomaly_type=f"Revenue {anomaly_type}",
                severity=severity,
                date=row['order_date'],
                region="All" # Simplified for now
            )
            db.add(anom)
    db.commit()
    
    return get_anomalies(db)

def get_anomalies(db: Session):
    anomalies = db.query(Anomaly).order_by(Anomaly.date.desc()).limit(20).all()
    return [{"date": str(a.date), "type": a.anomaly_type, "severity": a.severity, "region": a.region} for a in anomalies]
