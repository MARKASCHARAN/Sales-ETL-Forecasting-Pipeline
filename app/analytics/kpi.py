from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.schema import Order, OrderItem, Product, Customer
import pandas as pd

def get_total_revenue(db: Session) -> float:
    return db.query(func.sum(Order.total_amount)).scalar() or 0.0

def get_total_profit(db: Session) -> float:
    return db.query(func.sum(Order.profit)).scalar() or 0.0

def get_profit_margin(db: Session) -> float:
    revenue = get_total_revenue(db)
    profit = get_total_profit(db)
    if revenue == 0:
        return 0.0
    return (profit / revenue) * 100

def get_average_order_value(db: Session) -> float:
    return db.query(func.avg(Order.total_amount)).scalar() or 0.0

def get_top_products(db: Session, limit: int = 5):
    # Top products by quantity sold
    results = db.query(
        Product.category,
        Product.sub_category,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue')
    ).join(OrderItem, Product.product_id == OrderItem.product_id) \
     .group_by(Product.category, Product.sub_category) \
     .order_by(func.sum(OrderItem.quantity).desc()) \
     .limit(limit).all()
     
    return [{"category": r[0], "sub_category": r[1], "total_sold": r[2], "total_revenue": r[3]} for r in results]

def get_monthly_revenue(db: Session):
    # For SQLite compatibility, let's just pull it into pandas if it's tricky, or use extract
    # SQLite has strftime, Postgres has extract. Let's use string formatting for SQLite since we default to it.
    orders = db.query(Order.order_date, Order.total_amount).all()
    if not orders:
        return []
    
    df = pd.DataFrame([(o.order_date, o.total_amount) for o in orders], columns=['order_date', 'total_amount'])
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['month_year'] = df['order_date'].dt.to_period('M')
    monthly = df.groupby('month_year')['total_amount'].sum().reset_index()
    monthly['month_year'] = monthly['month_year'].astype(str)
    
    return monthly.to_dict('records')
