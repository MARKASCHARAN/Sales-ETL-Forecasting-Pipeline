import pandas as pd
from prophet import Prophet
from sqlalchemy.orm import Session
from app.models.schema import Order, SalesForecast
from datetime import datetime, timedelta

def generate_forecast(db: Session, periods: int = 30):
    orders = db.query(Order.order_date, Order.total_amount).all()
    if not orders:
        return []

    df = pd.DataFrame([(o.order_date, o.total_amount) for o in orders], columns=['order_date', 'total_amount'])
    df['order_date'] = pd.to_datetime(df['order_date']).dt.date
    daily_sales = df.groupby('order_date')['total_amount'].sum().reset_index()
    
    # Prophet requires 'ds' and 'y' columns
    prophet_df = daily_sales.rename(columns={'order_date': 'ds', 'total_amount': 'y'})
    
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(prophet_df)
    
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    # Extract only future dates
    last_date = prophet_df['ds'].max()
    future_forecast = forecast[forecast['ds'].dt.date > last_date]
    
    # Store in DB
    for _, row in future_forecast.iterrows():
        # check if exists
        existing = db.query(SalesForecast).filter(SalesForecast.forecast_date == row['ds'].date()).first()
        if not existing:
            sf = SalesForecast(
                forecast_date=row['ds'].date(),
                predicted_revenue=row['yhat'],
                model_name="Prophet"
            )
            db.add(sf)
    db.commit()
    
    # Return formatted forecast
    result = future_forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'predicted_revenue'})
    result['date'] = result['date'].dt.strftime('%Y-%m-%d')
    return result.to_dict('records')

def get_forecast(db: Session):
    forecasts = db.query(SalesForecast).order_by(SalesForecast.forecast_date).all()
    if not forecasts:
        return generate_forecast(db)
    return [{"date": str(f.forecast_date), "predicted_revenue": f.predicted_revenue, "model": f.model_name} for f in forecasts]
