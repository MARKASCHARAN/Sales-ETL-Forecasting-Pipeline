from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Region(Base):
    __tablename__ = "regions"
    
    region_id = Column(String, primary_key=True, index=True)
    state = Column(String, index=True)
    city = Column(String, index=True)
    zone = Column(String, index=True)

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    region_id = Column(String, ForeignKey("regions.region_id"))
    signup_date = Column(Date)
    age = Column(Integer)
    gender = Column(String)
    segment = Column(String, default="New") # Premium, Loyal, At Risk, Churn Risk, New, Low Value
    
    orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(String, primary_key=True, index=True)
    category = Column(String, index=True)
    sub_category = Column(String)
    stock = Column(Integer, default=0)
    price = Column(Float)
    
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float)
    payment_type = Column(String)
    shipping_cost = Column(Float)
    profit = Column(Float)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String, ForeignKey("orders.order_id"))
    product_id = Column(String, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    price = Column(Float)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class SalesForecast(Base):
    __tablename__ = "sales_forecast"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    forecast_date = Column(Date, index=True)
    predicted_revenue = Column(Float)
    model_name = Column(String) # Linear Regression, ARIMA, Prophet

class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    anomaly_type = Column(String) # sudden revenue drop, fake spikes, etc.
    severity = Column(String) # High, Medium, Low
    date = Column(Date, index=True)
    region = Column(String)
