"""
Northwind Database Setup Script
Creates and populates a SQLite database with sample business data.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'northwind.db')


def create_connection():
    """Create a database connection to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn


def create_tables(conn):
    """Create all necessary tables with proper schemas."""
    cursor = conn.cursor()
    
    print("Creating tables...")
    
    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            CustomerID TEXT PRIMARY KEY,
            CompanyName TEXT NOT NULL,
            ContactName TEXT NOT NULL,
            Country TEXT NOT NULL,
            City TEXT NOT NULL,
            Phone TEXT
        )
    """)
    
    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProductName TEXT NOT NULL,
            CategoryName TEXT NOT NULL,
            UnitPrice REAL NOT NULL,
            UnitsInStock INTEGER NOT NULL
        )
    """)
    
    # Employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employees (
            EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            Title TEXT NOT NULL,
            HireDate TEXT NOT NULL
        )
    """)
    
    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
            CustomerID TEXT NOT NULL,
            EmployeeID INTEGER NOT NULL,
            OrderDate TEXT NOT NULL,
            ShippedDate TEXT,
            ShipCountry TEXT NOT NULL,
            Freight REAL NOT NULL,
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
            FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
        )
    """)
    
    # OrderDetails table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS OrderDetails (
            OrderDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER NOT NULL,
            ProductID INTEGER NOT NULL,
            Quantity INTEGER NOT NULL,
            UnitPrice REAL NOT NULL,
            Discount REAL DEFAULT 0,
            FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        )
    """)
    
    conn.commit()
    print("✓ Tables created successfully")


def populate_customers(conn):
    """Populate Customers table with sample data."""
    cursor = conn.cursor()
    
    customers = [
        ('ALFKI', 'Alfreds Futterkiste', 'Maria Anders', 'Germany', 'Berlin', '030-0074321'),
        ('ANATR', 'Ana Trujillo Emparedados', 'Ana Trujillo', 'Mexico', 'México D.F.', '(5) 555-4729'),
        ('ANTON', 'Antonio Moreno Taquería', 'Antonio Moreno', 'Mexico', 'México D.F.', '(5) 555-3932'),
        ('AROUT', 'Around the Horn', 'Thomas Hardy', 'UK', 'London', '(171) 555-7788'),
        ('BERGS', 'Berglunds snabbköp', 'Christina Berglund', 'Sweden', 'Luleå', '0921-12 34 65'),
        ('BLAUS', 'Blauer See Delikatessen', 'Hanna Moos', 'Germany', 'Mannheim', '0621-08460'),
        ('BLONP', 'Blondesddsl père et fils', 'Frédérique Citeaux', 'France', 'Strasbourg', '88.60.15.31'),
        ('BOLID', 'Bólido Comidas preparadas', 'Martín Sommer', 'Spain', 'Madrid', '(91) 555 22 82'),
        ('BONAP', 'Bon app', 'Laurence Lebihan', 'France', 'Marseille', '91.24.45.40'),
        ('BOTTM', 'Bottom-Dollar Markets', 'Elizabeth Lincoln', 'Canada', 'Tsawassen', '(604) 555-4729'),
        ('BSBEV', 'B\'s Beverages', 'Victoria Ashworth', 'UK', 'London', '(171) 555-1212'),
        ('CACTU', 'Cactus Comidas para llevar', 'Patricio Simpson', 'Argentina', 'Buenos Aires', '(1) 135-5555'),
        ('CENTC', 'Centro comercial Moctezuma', 'Francisco Chang', 'Mexico', 'México D.F.', '(5) 555-3392'),
        ('CHOPS', 'Chop-suey Chinese', 'Yang Wang', 'Switzerland', 'Bern', '0452-076545'),
        ('COMMI', 'Comércio Mineiro', 'Pedro Afonso', 'Brazil', 'São Paulo', '(11) 555-7647'),
        ('CONSH', 'Consolidated Holdings', 'Elizabeth Brown', 'UK', 'London', '(171) 555-2282'),
        ('DRACD', 'Drachenblut Delikatessen', 'Sven Ottlieb', 'Germany', 'Aachen', '0241-039123'),
        ('DUMON', 'Du monde entier', 'Janine Labrune', 'France', 'Nantes', '40.67.88.88'),
        ('EASTC', 'Eastern Connection', 'Ann Devon', 'UK', 'London', '(171) 555-0297'),
        ('ERNSH', 'Ernst Handel', 'Roland Mendel', 'Austria', 'Graz', '7675-3425'),
        ('FAMIA', 'Familia Arquibaldo', 'Aria Cruz', 'Brazil', 'São Paulo', '(11) 555-9857'),
        ('FISSA', 'FISSA Fabrica Inter. Salchichas', 'Diego Roel', 'Spain', 'Madrid', '(91) 555 94 44'),
        ('FOLIG', 'Folies gourmandes', 'Martine Rancé', 'France', 'Lille', '20.16.10.16'),
        ('FOLKO', 'Folk och fä HB', 'Maria Larsson', 'Sweden', 'Bräcke', '0695-34 67 21'),
        ('FRANK', 'Frankenversand', 'Peter Franken', 'Germany', 'München', '089-0877310'),
        ('FRANR', 'France restauration', 'Carine Schmitt', 'France', 'Nantes', '40.32.21.21'),
        ('FRANS', 'Franchi S.p.A.', 'Paolo Accorti', 'Italy', 'Torino', '011-4988260'),
        ('FURIB', 'Furia Bacalhau e Frutos do Mar', 'Lino Rodriguez', 'Portugal', 'Lisboa', '(1) 354-2534'),
        ('GALED', 'Galería del gastrónomo', 'Eduardo Saavedra', 'Spain', 'Barcelona', '(93) 203 4560'),
        ('GODOS', 'Godos Cocina Típica', 'José Pedro Freyre', 'Spain', 'Sevilla', '(95) 555 82 82'),
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO Customers VALUES (?, ?, ?, ?, ?, ?)",
        customers
    )
    conn.commit()
    print(f"✓ Inserted {len(customers)} customers")


def populate_products(conn):
    """Populate Products table with sample data."""
    cursor = conn.cursor()
    
    products = [
        ('Chai', 'Beverages', 18.00, 39),
        ('Chang', 'Beverages', 19.00, 17),
        ('Aniseed Syrup', 'Condiments', 10.00, 13),
        ('Chef Anton\'s Cajun Seasoning', 'Condiments', 22.00, 53),
        ('Chef Anton\'s Gumbo Mix', 'Condiments', 21.35, 0),
        ('Grandma\'s Boysenberry Spread', 'Condiments', 25.00, 120),
        ('Uncle Bob\'s Organic Dried Pears', 'Produce', 30.00, 15),
        ('Northwoods Cranberry Sauce', 'Condiments', 40.00, 6),
        ('Mishi Kobe Niku', 'Meat/Poultry', 97.00, 29),
        ('Ikura', 'Seafood', 31.00, 31),
        ('Queso Cabrales', 'Dairy Products', 21.00, 22),
        ('Queso Manchego La Pastora', 'Dairy Products', 38.00, 86),
        ('Konbu', 'Seafood', 6.00, 24),
        ('Tofu', 'Produce', 23.25, 35),
        ('Genen Shouyu', 'Condiments', 15.50, 39),
        ('Pavlova', 'Confections', 17.45, 29),
        ('Alice Mutton', 'Meat/Poultry', 39.00, 0),
        ('Carnarvon Tigers', 'Seafood', 62.50, 42),
        ('Teatime Chocolate Biscuits', 'Confections', 9.20, 25),
        ('Sir Rodney\'s Marmalade', 'Confections', 81.00, 40),
        ('Sir Rodney\'s Scones', 'Confections', 10.00, 3),
        ('Gustaf\'s Knäckebröd', 'Grains/Cereals', 21.00, 104),
        ('Tunnbröd', 'Grains/Cereals', 9.00, 61),
        ('Guaraná Fantástica', 'Beverages', 4.50, 20),
        ('NuNuCa Nuß-Nougat-Creme', 'Confections', 14.00, 76),
        ('Gumbär Gummibärchen', 'Confections', 31.23, 15),
        ('Schoggi Schokolade', 'Confections', 43.90, 49),
        ('Rössle Sauerkraut', 'Produce', 45.60, 26),
        ('Thüringer Rostbratwurst', 'Meat/Poultry', 123.79, 0),
        ('Nord-Ost Matjeshering', 'Seafood', 25.89, 10),
    ]
    
    cursor.executemany(
        "INSERT INTO Products (ProductName, CategoryName, UnitPrice, UnitsInStock) VALUES (?, ?, ?, ?)",
        products
    )
    conn.commit()
    print(f"✓ Inserted {len(products)} products")


def populate_employees(conn):
    """Populate Employees table with sample data."""
    cursor = conn.cursor()
    
    employees = [
        ('Nancy', 'Davolio', 'Sales Representative', '2020-05-01'),
        ('Andrew', 'Fuller', 'Vice President, Sales', '2019-08-14'),
        ('Janet', 'Leverling', 'Sales Representative', '2020-04-01'),
        ('Margaret', 'Peacock', 'Sales Representative', '2021-05-03'),
        ('Steven', 'Buchanan', 'Sales Manager', '2019-10-17'),
        ('Michael', 'Suyama', 'Sales Representative', '2021-10-17'),
        ('Robert', 'King', 'Sales Representative', '2022-01-02'),
        ('Laura', 'Callahan', 'Inside Sales Coordinator', '2022-03-05'),
        ('Anne', 'Dodsworth', 'Sales Representative', '2022-11-15'),
        ('John', 'Smith', 'Sales Representative', '2023-02-01'),
    ]
    
    cursor.executemany(
        "INSERT INTO Employees (FirstName, LastName, Title, HireDate) VALUES (?, ?, ?, ?)",
        employees
    )
    conn.commit()
    print(f"✓ Inserted {len(employees)} employees")


def populate_orders_and_details(conn):
    """Populate Orders and OrderDetails tables with sample data."""
    cursor = conn.cursor()
    
    # Get all customer IDs, employee IDs, and product IDs
    cursor.execute("SELECT CustomerID FROM Customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT EmployeeID FROM Employees")
    employee_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT ProductID, UnitPrice FROM Products")
    products = cursor.fetchall()
    
    # Generate orders spanning 2023-2024
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days
    
    orders_count = 100
    print(f"Generating {orders_count} orders with details...")
    
    for i in range(orders_count):
        # Random order date
        order_date = start_date + timedelta(days=random.randint(0, date_range))
        
        # Shipped date: 70% on time (3-7 days), 30% late (8-15 days)
        if random.random() < 0.7:
            days_to_ship = random.randint(3, 7)
        else:
            days_to_ship = random.randint(8, 15)
        
        shipped_date = order_date + timedelta(days=days_to_ship)
        
        # Random customer, employee, and freight
        customer_id = random.choice(customer_ids)
        employee_id = random.choice(employee_ids)
        freight = round(random.uniform(5.0, 150.0), 2)
        
        # Get customer's country
        cursor.execute("SELECT Country FROM Customers WHERE CustomerID = ?", (customer_id,))
        ship_country = cursor.fetchone()[0]
        
        # Insert order
        cursor.execute("""
            INSERT INTO Orders (CustomerID, EmployeeID, OrderDate, ShippedDate, ShipCountry, Freight)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (customer_id, employee_id, order_date.strftime('%Y-%m-%d'), 
              shipped_date.strftime('%Y-%m-%d'), ship_country, freight))
        
        order_id = cursor.lastrowid
        
        # Add 1-5 order details per order
        num_details = random.randint(1, 5)
        selected_products = random.sample(products, min(num_details, len(products)))
        
        for product_id, unit_price in selected_products:
            quantity = random.randint(1, 50)
            # 20% chance of discount (5%, 10%, 15%, or 20%)
            discount = random.choice([0, 0, 0, 0, 0.05, 0.10, 0.15, 0.20])
            
            cursor.execute("""
                INSERT INTO OrderDetails (OrderID, ProductID, Quantity, UnitPrice, Discount)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, product_id, quantity, unit_price, discount))
    
    conn.commit()
    print(f"✓ Inserted {orders_count} orders with order details")


def print_summary(conn):
    """Print summary of records in each table."""
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("DATABASE SUMMARY")
    print("="*50)
    
    tables = ['Customers', 'Products', 'Employees', 'Orders', 'OrderDetails']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:20} {count:>5} records")
    
    print("="*50)
    print(f"\nDatabase created successfully at: {DB_PATH}")


def main():
    """Main function to set up the database."""
    print("\n" + "="*50)
    print("NORTHWIND DATABASE SETUP")
    print("="*50 + "\n")
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        print(f"Removing existing database: {DB_PATH}")
        os.remove(DB_PATH)
    
    # Create connection and set up database
    conn = create_connection()
    
    try:
        create_tables(conn)
        populate_customers(conn)
        populate_products(conn)
        populate_employees(conn)
        populate_orders_and_details(conn)
        print_summary(conn)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
    
    print("\n✅ Setup completed successfully!\n")


if __name__ == "__main__":
    main()

