import mysql.connector
from faker import Faker
import random
import os
from dotenv import load_dotenv

#  Load environment variables
load_dotenv(dotenv_path="key.env")

#  Connect to MySQL and create DB if missing
def get_connection():
    # First connect without selecting a DB
    base_conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    base_cursor = base_conn.cursor()
    base_cursor.execute("CREATE DATABASE IF NOT EXISTS shopmart")
    base_cursor.close()
    base_conn.close()

    # Then connect with DB
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

#  Create required tables
def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        customer_id INT PRIMARY KEY AUTO_INCREMENT,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100),
        sign_up_date DATE,
        region VARCHAR(50)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        product_id INT PRIMARY KEY AUTO_INCREMENT,
        product_name VARCHAR(100),
        category VARCHAR(50),
        price DECIMAL(10, 2)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INT PRIMARY KEY AUTO_INCREMENT,
        customer_id INT,
        order_date DATE,
        order_status VARCHAR(20),
        total_amount DECIMAL(10, 2),
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OrderDetails (
        order_id INT,
        product_id INT,
        quantity INT,
        PRIMARY KEY (order_id, product_id),
        FOREIGN KEY (order_id) REFERENCES Orders(order_id),
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    );
    """)

#  Populate database with Faker data
def populate_data(cursor, db):
    fake = Faker()
    regions = ['North', 'South', 'East', 'West']

    # Customers
    for _ in range(1000):
        first = fake.first_name()
        last = fake.last_name()
        email = f"{first.lower()}.{last.lower()}@{fake.domain_name()}"
        sign_up_date = fake.date_between(start_date='-5y', end_date='today')
        region = random.choice(regions)

        cursor.execute("""
        INSERT INTO Customers (first_name, last_name, email, sign_up_date, region)
        VALUES (%s, %s, %s, %s, %s)
        """, (first, last, email, sign_up_date, region))
    db.commit()

    # Products
    categories = ['Electronics', 'Clothing', 'Home Goods', 'Books', 'Toys']
    for _ in range(100):
        name = f"{fake.word().capitalize()} {fake.word().capitalize()}"
        category = random.choice(categories)
        price = round(random.uniform(5.00, 1000.00), 2)

        cursor.execute("""
        INSERT INTO Products (product_name, category, price)
        VALUES (%s, %s, %s)
        """, (name, category, price))
    db.commit()

    # Orders and OrderDetails
    for _ in range(2500):
        customer_id = random.randint(1, 1000)
        order_date = fake.date_between(start_date='-1y', end_date='today')
        order_status = random.choice(['Completed', 'Pending', 'Canceled'])

        cursor.execute("""
        INSERT INTO Orders (customer_id, order_date, order_status, total_amount)
        VALUES (%s, %s, %s, %s)
        """, (customer_id, order_date, order_status, 0.00))
        order_id = cursor.lastrowid

        total = 0.0
        product_ids_used = set()

        for _ in range(random.randint(1, 5)):
            prod_id = random.randint(1, 100)
            while prod_id in product_ids_used:
                prod_id = random.randint(1, 100)
            product_ids_used.add(prod_id)

            quantity = random.randint(1, 10)
            cursor.execute("SELECT price FROM Products WHERE product_id = %s", (prod_id,))
            result = cursor.fetchone()

            if result:
                price = float(result[0])
                total += price * quantity

                cursor.execute("""
                INSERT INTO OrderDetails (order_id, product_id, quantity)
                VALUES (%s, %s, %s)
                """, (order_id, prod_id, quantity))

        cursor.execute("""
        UPDATE Orders SET total_amount = %s WHERE order_id = %s
        """, (total, order_id))

    db.commit()

# Main runner
def main():
    print("HOST:", os.getenv("DB_HOST")) 
    conn = get_connection()
    print("Connection successful")     
    cursor = conn.cursor()
    create_tables(cursor)
    print("Tables created")             
    populate_data(cursor, conn)
    print("Data populated")            
    cursor.close()
    conn.close()
    print("Database seeded successfully!") 


if __name__ == "__main__":
    main()
