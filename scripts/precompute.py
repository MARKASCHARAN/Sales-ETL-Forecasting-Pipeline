from app.database import SessionLocal
from app.customer_intelligence.rfm import calculate_rfm
from app.forecasting.predict import generate_forecast
from app.anomaly.detect import detect_anomalies

def run_precompute():
    print("Starting precomputation...")
    db = SessionLocal()
    try:
        print("Calculating RFM Segments...")
        calculate_rfm(db)
        print("Generating Sales Forecast...")
        generate_forecast(db)
        print("Detecting Anomalies...")
        detect_anomalies(db)
        print("Precomputation finished successfully!")
    except Exception as e:
        print(f"Error during precomputation: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_precompute()
