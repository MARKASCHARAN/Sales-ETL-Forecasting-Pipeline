import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.models import schema
from app.database import engine, SessionLocal
import os

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Remove duplicates
    df = df.drop_duplicates(subset=['customer_id'])
    
    # 2. Fill missing values
    df['email'] = df['email'].fillna('unknown@example.com')
    df['region_id'] = df['region_id'].fillna('R1') # default to R1
    
    # 3. Normalize text
    df['name'] = df['name'].str.title()
    
    # 4. Handle Age & Gender
    df['age'] = df['age'].fillna(df['age'].median())
    df['gender'] = df['gender'].fillna('Other')
    
    return df

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=['order_id'])
    
    # Fill missing total_amount based on something or just median/0 for now
    # Ideally, we should recalculate it from order_items, but let's do a simple fill
    df['total_amount'] = df['total_amount'].fillna(df['total_amount'].median())
    df['payment_type'] = df['payment_type'].fillna('Unknown')
    
    # Ensure dates are datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    return df

def run_etl():
    print("Starting ETL process...")
    
    # Extract
    raw_dir = "datasets/raw"
    if not os.path.exists(raw_dir):
        print("No raw data found. Please run generate_dummy_data.py first.")
        return
        
    customers_df = pd.read_csv(f"{raw_dir}/customers.csv")
    orders_df = pd.read_csv(f"{raw_dir}/orders.csv")
    order_items_df = pd.read_csv(f"{raw_dir}/order_items.csv")
    products_df = pd.read_csv(f"{raw_dir}/products.csv")
    regions_df = pd.read_csv(f"{raw_dir}/regions.csv")
    
    # Transform
    print("Transforming data...")
    clean_customers_df = clean_customers(customers_df)
    clean_orders_df = clean_orders(orders_df)
    
    # Clean others lightly
    products_df = products_df.drop_duplicates(subset=['product_id'])
    regions_df = regions_df.drop_duplicates(subset=['region_id'])
    order_items_df = order_items_df.drop_duplicates()
    
    # Load
    print("Loading data into DB...")
    db: Session = SessionLocal()
    
    try:
        # Load Regions
        for _, row in regions_df.iterrows():
            if not db.query(schema.Region).filter_by(region_id=row['region_id']).first():
                db.add(schema.Region(**row.to_dict()))
        db.commit()
        
        # Load Products
        for _, row in products_df.iterrows():
            if not db.query(schema.Product).filter_by(product_id=row['product_id']).first():
                db.add(schema.Product(**row.to_dict()))
        db.commit()
        
        # Load Customers
        for _, row in clean_customers_df.iterrows():
            if not db.query(schema.Customer).filter_by(customer_id=row['customer_id']).first():
                db.add(schema.Customer(**row.to_dict()))
        db.commit()
        
        # Load Orders
        for _, row in clean_orders_df.iterrows():
            if not db.query(schema.Order).filter_by(order_id=row['order_id']).first():
                db.add(schema.Order(**row.to_dict()))
        db.commit()
        
        # Load Order Items
        for _, row in order_items_df.iterrows():
            db.add(schema.OrderItem(**row.to_dict()))
        db.commit()
        
        print("ETL process completed successfully!")
    except Exception as e:
        print(f"Error during Load: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_etl()
