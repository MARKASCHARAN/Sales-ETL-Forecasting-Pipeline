import pandas as pd
import numpy as np
from faker import Faker
import os
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def generate_data(num_customers=500, num_products=50, num_orders=5000):
    os.makedirs("datasets/raw", exist_ok=True)
    
    # 1. Regions
    regions_data = [
        {"region_id": "R1", "state": "California", "city": "San Francisco", "zone": "West"},
        {"region_id": "R2", "state": "California", "city": "Los Angeles", "zone": "West"},
        {"region_id": "R3", "state": "New York", "city": "New York", "zone": "East"},
        {"region_id": "R4", "state": "Texas", "city": "Austin", "zone": "South"},
        {"region_id": "R5", "state": "Illinois", "city": "Chicago", "zone": "Midwest"}
    ]
    regions_df = pd.DataFrame(regions_data)
    regions_df.to_csv("datasets/raw/regions.csv", index=False)

    # 2. Customers
    customers = []
    for i in range(num_customers):
        # Intro some "dirty" data like missing age, gender
        customers.append({
            "customer_id": f"C{i+1:04d}",
            "name": fake.name(),
            "email": fake.email() if random.random() > 0.05 else None, # 5% missing email
            "region_id": random.choice(["R1", "R2", "R3", "R4", "R5", None]), # some missing regions
            "signup_date": fake.date_between(start_date="-3y", end_date="today").isoformat(),
            "age": random.randint(18, 70) if random.random() > 0.1 else np.nan,
            "gender": random.choice(["Male", "Female", "Other", None])
        })
    customers_df = pd.DataFrame(customers)
    # Add some duplicates
    customers_df = pd.concat([customers_df, customers_df.sample(10)]).reset_index(drop=True)
    customers_df.to_csv("datasets/raw/customers.csv", index=False)

    # 3. Products
    categories = ["Electronics", "Clothing", "Home", "Sports", "Toys"]
    products = []
    for i in range(num_products):
        products.append({
            "product_id": f"P{i+1:03d}",
            "category": random.choice(categories),
            "sub_category": fake.word(),
            "stock": random.randint(10, 500),
            "price": round(random.uniform(10.0, 1000.0), 2)
        })
    products_df = pd.DataFrame(products)
    products_df.to_csv("datasets/raw/products.csv", index=False)

    # 4. Orders & Order Items
    orders = []
    order_items = []
    
    start_date = datetime.now() - timedelta(days=730)
    
    for i in range(num_orders):
        order_id = f"O{i+1:05d}"
        customer_id = random.choice(customers)["customer_id"]
        order_date = start_date + timedelta(days=random.randint(0, 730), hours=random.randint(0, 23))
        
        # 1 to 5 items per order
        num_items = random.randint(1, 5)
        total_amount = 0
        total_cost = 0
        
        for _ in range(num_items):
            prod = random.choice(products)
            qty = random.randint(1, 5)
            price = prod["price"]
            
            total_amount += (qty * price)
            total_cost += (qty * price * random.uniform(0.5, 0.8)) # random cost margin
            
            order_items.append({
                "order_id": order_id,
                "product_id": prod["product_id"],
                "quantity": qty,
                "price": price
            })
            
        payment_type = random.choice(["Credit Card", "PayPal", "Debit Card", None])
        shipping_cost = round(random.uniform(5.0, 50.0), 2)
        profit = round(total_amount - total_cost - shipping_cost, 2)
        
        # introduce some dirty data
        if random.random() < 0.02:
            total_amount = np.nan
        
        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date.isoformat(),
            "total_amount": round(total_amount, 2) if not pd.isna(total_amount) else total_amount,
            "payment_type": payment_type,
            "shipping_cost": shipping_cost,
            "profit": profit
        })
        
    orders_df = pd.DataFrame(orders)
    order_items_df = pd.DataFrame(order_items)
    
    orders_df.to_csv("datasets/raw/orders.csv", index=False)
    order_items_df.to_csv("datasets/raw/order_items.csv", index=False)

    print("Dummy data generated successfully in datasets/raw/")

if __name__ == "__main__":
    generate_data()
