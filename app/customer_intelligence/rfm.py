import pandas as pd
from sqlalchemy.orm import Session
from app.models.schema import Order, Customer
import numpy as np

def calculate_rfm(db: Session):
    orders = db.query(Order.customer_id, Order.order_date, Order.total_amount).all()
    if not orders:
        return pd.DataFrame()
        
    df = pd.DataFrame([(o.customer_id, o.order_date, o.total_amount) for o in orders], 
                      columns=['customer_id', 'order_date', 'total_amount'])
    
    df['order_date'] = pd.to_datetime(df['order_date'])
    latest_date = df['order_date'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (latest_date - x.max()).days,
        'customer_id': 'count',
        'total_amount': 'sum'
    }).rename(columns={
        'order_date': 'Recency',
        'customer_id': 'Frequency',
        'total_amount': 'Monetary'
    }).reset_index()
    
    # Create RFM Scores (1-4)
    # R is inverted (lower recency is better)
    rfm['R'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1], duplicates='drop')
    
    # Some customers might have same frequency, drop duplicates or use rank
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    rfm['M'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])
    
    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
    
    def segment_customer(score):
        if score == '444':
            return 'Premium'
        elif score.startswith('4') or score.startswith('3'):
            return 'Loyal'
        elif score.startswith('1') and int(score[1]) > 2:
            return 'At Risk'
        elif score.startswith('1') and int(score[1]) <= 2:
            return 'Churn Risk'
        elif score.startswith('2'):
            return 'New'
        else:
            return 'Low Value'
            
    rfm['Segment'] = rfm['RFM_Score'].apply(segment_customer)
    
    # Update DB
    for _, row in rfm.iterrows():
        customer = db.query(Customer).filter_by(customer_id=row['customer_id']).first()
        if customer:
            customer.segment = row['Segment']
    db.commit()
    
    return rfm

def get_segments(db: Session):
    segments = db.query(Customer.segment).all()
    df = pd.DataFrame(segments, columns=['segment'])
    return df['segment'].value_counts().to_dict()
