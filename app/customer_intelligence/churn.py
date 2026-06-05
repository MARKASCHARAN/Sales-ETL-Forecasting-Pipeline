import pandas as pd
from sqlalchemy.orm import Session
from app.models.schema import Order, Customer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from app.customer_intelligence.rfm import calculate_rfm

def predict_churn(db: Session):
    rfm_df = calculate_rfm(db)
    if rfm_df.empty:
        return []
        
    # Let's define Churn = Recency > 180 days for training labels
    rfm_df['is_churned'] = (rfm_df['Recency'] > 180).astype(int)
    
    features = ['Recency', 'Frequency', 'Monetary']
    X = rfm_df[features]
    y = rfm_df['is_churned']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Simple Random Forest for prediction
    model = RandomForestClassifier(random_state=42, n_estimators=50)
    model.fit(X_scaled, y)
    
    rfm_df['churn_probability'] = model.predict_proba(X_scaled)[:, 1]
    
    # Get those at high risk but haven't actually churned yet (e.g. recency < 180 but high prob)
    # Or just returning top high risk customers overall
    high_risk = rfm_df[rfm_df['churn_probability'] > 0.7].sort_values(by='churn_probability', ascending=False)
    
    return high_risk[['customer_id', 'churn_probability', 'Recency', 'Frequency']].to_dict('records')

def get_clv(db: Session):
    rfm_df = calculate_rfm(db)
    if rfm_df.empty:
        return []
    
    # Simple CLV = Average Order Value * Frequency (in a year) * Average Lifespan
    # For simplicity, we just use Monetary * some multiplier based on Recency
    rfm_df['CLV'] = rfm_df['Monetary'] * (1.0 + (365 - rfm_df['Recency']) / 365)
    rfm_df['CLV'] = rfm_df['CLV'].apply(lambda x: max(0, x)) # Ensure non-negative
    
    top_clv = rfm_df.sort_values(by='CLV', ascending=False).head(10)
    return top_clv[['customer_id', 'CLV', 'Segment']].to_dict('records')
