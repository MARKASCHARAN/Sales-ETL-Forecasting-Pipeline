# SalesPulse – Real-Time Sales Analytics, Forecasting & Customer Intelligence Platform

SalesPulse is a complete, real-time analytics pipeline and dashboard designed to help companies understand their sales, forecast future revenue, identify churn risks, and detect anomalies. It serves as a unified backend and data science module exposing APIs and a visualization interface.

## 🚀 Key Features

*   **Data Ingestion & ETL**: Scripts to mock and transform raw, dirty business data (Orders, Products, Customers, Regions) and load it cleanly into the database.
*   **KPI Analytics Engine**: Calculates real-time metrics including total revenue, profit margins, average order value, and top products.
*   **Customer Intelligence**:
    *   **RFM Segmentation**: Classifies customers into segments (Premium, Loyal, At Risk, Churn Risk, New, Low Value).
    *   **Churn Prediction**: Uses Random Forest to predict the likelihood of customers churning.
    *   **Customer Lifetime Value (CLV)**: Estimates the total value of top customers.
*   **Forecasting Engine**: Leverages Facebook Prophet for time-series forecasting of future daily revenue.
*   **Anomaly Detection Engine**: Detects statistical anomalies (spikes and drops) in daily sales using Z-Score.
*   **Executive Dashboard**: Built with Streamlit and Plotly for high-quality, interactive visualization.
*   **RESTful APIs**: Powered by FastAPI, acting as a decoupled backend.

## 🛠️ Tech Stack

*   **Backend / API**: Python, FastAPI
*   **Data & ML**: Pandas, NumPy, Scikit-Learn, Prophet
*   **Database**: SQLite (default for easy setup) / PostgreSQL via SQLAlchemy & Alembic
*   **Visualization**: Streamlit, Plotly
*   **Infrastructure**: Docker, Docker Compose

## 📁 Project Structure

```bash
Sales-ETL-Forecasting-Pipeline/
├── app/
│   ├── api/                     # FastAPI Routers
│   ├── analytics/               # KPI aggregations
│   ├── anomaly/                 # Anomaly detection logic
│   ├── customer_intelligence/   # RFM, Churn, CLV logic
│   ├── forecasting/             # Prophet modeling
│   ├── ingestion/               # ETL Pipeline
│   ├── models/                  # SQLAlchemy schemas
│   ├── database.py              # DB Connection
│   └── main.py                  # FastAPI Application Entry
├── dashboard/
│   └── app.py                   # Streamlit Frontend
├── datasets/raw/                # Generated Mock Datasets
├── scripts/
│   ├── generate_dummy_data.py   # Data Generation
│   └── precompute.py            # Precomputes ML metrics to DB
├── docker-compose.yml           
├── Dockerfile                   
└── requirements.txt             
```

## ⚙️ How to Run Locally

### 1. Set Up Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=.
```

### 2. Generate Data & Run ETL
```bash
# Generates dirty mock data
python scripts/generate_dummy_data.py

# Cleans and loads data into SQLite
python app/ingestion/etl.py

# Precompute ML metrics (RFM, Forecasts, Anomalies)
python scripts/precompute.py
```

### 3. Run FastAPI Backend
```bash
uvicorn app.main:app --reload
```
API Documentation available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run Streamlit Dashboard (In a new terminal)
```bash
source venv/bin/activate
export PYTHONPATH=.
streamlit run dashboard/app.py
```
Dashboard available at: [http://localhost:8501](http://localhost:8501)

## 🐳 How to Run with Docker

```bash
docker-compose up --build
```
This spins up both the FastAPI backend and Streamlit dashboard automatically.

## 📊 Modules Breakdown

### Module 1 & 2: Ingestion & ETL
Reads mocked CSVs, normalizes strings, handles NaNs, computes profit, and drops duplicates before saving to the SQL DB via SQLAlchemy.

### Module 3: KPI Engine
Aggregates SQL queries for revenue, profit margins, monthly trends, and top products.

### Module 4: Customer Intelligence
Computes R, F, M quartiles, assigns customer segments, uses Scikit-Learn to predict churn probabilities, and ranks customers by CLV.

### Module 5: Forecasting
Uses `prophet` to decompose trends and seasonality on historical sales, projecting the next 30 days of revenue.

### Module 6: Anomaly Detection
Calculates the mean and standard deviation of daily sales, flagging any days with a Z-Score greater than 2 as a Spike or Drop.

### Module 7: Visualization
Interactive Streamlit application polling the FastAPI backend to visualize the data efficiently.
