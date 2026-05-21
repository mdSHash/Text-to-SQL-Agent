"""
Tests for database setup and structure.
"""

import unittest
import sqlite3
import os
from pathlib import Path


class TestDatabase(unittest.TestCase):
    """Test the database setup and structure."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.db_path = Path("data/northwind.db")
        
    def test_database_exists(self):
        """Check that data/northwind.db exists after running setup."""
        self.assertTrue(
            self.db_path.exists(),
            f"Database file not found at {self.db_path}. Run 'python data/setup_db.py' first."
        )
        
        # Verify it's a valid SQLite database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            self.assertGreater(len(tables), 0, "Database exists but has no tables")
        except sqlite3.DatabaseError as e:
            self.fail(f"File exists but is not a valid SQLite database: {e}")
    
    def test_tables_exist(self):
        """Verify all 5 tables exist with correct names."""
        expected_tables = {'Customers', 'Products', 'Employees', 'Orders', 'OrderDetails'}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        self.assertEqual(
            expected_tables,
            tables,
            f"Expected tables {expected_tables}, but found {tables}"
        )
    
    def test_table_schemas(self):
        """Verify each table has the expected columns and types."""
        expected_schemas = {
            'Customers': {
                'CustomerID': 'TEXT',
                'CompanyName': 'TEXT',
                'ContactName': 'TEXT',
                'Country': 'TEXT'
            },
            'Products': {
                'ProductID': 'INTEGER',
                'ProductName': 'TEXT',
                'CategoryID': 'INTEGER',
                'UnitPrice': 'REAL',
                'UnitsInStock': 'INTEGER'
            },
            'Employees': {
                'EmployeeID': 'INTEGER',
                'FirstName': 'TEXT',
                'LastName': 'TEXT',
                'Title': 'TEXT',
                'HireDate': 'TEXT'
            },
            'Orders': {
                'OrderID': 'INTEGER',
                'CustomerID': 'TEXT',
                'EmployeeID': 'INTEGER',
                'OrderDate': 'TEXT',
                'ShipCountry': 'TEXT'
            },
            'OrderDetails': {
                'OrderDetailID': 'INTEGER',
                'OrderID': 'INTEGER',
                'ProductID': 'INTEGER',
                'Quantity': 'INTEGER',
                'UnitPrice': 'REAL'
            }
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for table_name, expected_columns in expected_schemas.items():
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            for col_name, col_type in expected_columns.items():
                self.assertIn(
                    col_name,
                    columns,
                    f"Column {col_name} not found in table {table_name}"
                )
                self.assertEqual(
                    columns[col_name],
                    col_type,
                    f"Column {col_name} in {table_name} has type {columns[col_name]}, expected {col_type}"
                )
        
        conn.close()
    
    def test_primary_keys_exist(self):
        """Verify primary keys exist for each table."""
        expected_pks = {
            'Customers': 'CustomerID',
            'Products': 'ProductID',
            'Employees': 'EmployeeID',
            'Orders': 'OrderID',
            'OrderDetails': 'OrderDetailID'
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for table_name, expected_pk in expected_pks.items():
            cursor.execute(f"PRAGMA table_info({table_name});")
            pk_columns = [row[1] for row in cursor.fetchall() if row[5] > 0]  # row[5] is pk flag
            
            self.assertIn(
                expected_pk,
                pk_columns,
                f"Primary key {expected_pk} not found in table {table_name}"
            )
        
        conn.close()
    
    def test_data_populated(self):
        """Check each table has data with minimum expected row counts."""
        min_row_counts = {
            'Customers': 20,
            'Products': 10,
            'Employees': 5,
            'Orders': 20,
            'OrderDetails': 30
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for table_name, min_count in min_row_counts.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            
            self.assertGreater(
                count,
                0,
                f"Table {table_name} has no data"
            )
            self.assertGreaterEqual(
                count,
                min_count,
                f"Table {table_name} has {count} rows, expected at least {min_count}"
            )
        
        conn.close()
    
    def test_referential_integrity(self):
        """Verify foreign keys are valid."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test Orders.CustomerID references Customers.CustomerID
        cursor.execute("""
            SELECT COUNT(*) FROM Orders o
            LEFT JOIN Customers c ON o.CustomerID = c.CustomerID
            WHERE c.CustomerID IS NULL AND o.CustomerID IS NOT NULL;
        """)
        invalid_customers = cursor.fetchone()[0]
        self.assertEqual(
            invalid_customers,
            0,
            f"Found {invalid_customers} orders with invalid CustomerID"
        )
        
        # Test Orders.EmployeeID references Employees.EmployeeID
        cursor.execute("""
            SELECT COUNT(*) FROM Orders o
            LEFT JOIN Employees e ON o.EmployeeID = e.EmployeeID
            WHERE e.EmployeeID IS NULL AND o.EmployeeID IS NOT NULL;
        """)
        invalid_employees = cursor.fetchone()[0]
        self.assertEqual(
            invalid_employees,
            0,
            f"Found {invalid_employees} orders with invalid EmployeeID"
        )
        
        # Test OrderDetails.OrderID references Orders.OrderID
        cursor.execute("""
            SELECT COUNT(*) FROM OrderDetails od
            LEFT JOIN Orders o ON od.OrderID = o.OrderID
            WHERE o.OrderID IS NULL;
        """)
        invalid_orders = cursor.fetchone()[0]
        self.assertEqual(
            invalid_orders,
            0,
            f"Found {invalid_orders} order details with invalid OrderID"
        )
        
        # Test OrderDetails.ProductID references Products.ProductID
        cursor.execute("""
            SELECT COUNT(*) FROM OrderDetails od
            LEFT JOIN Products p ON od.ProductID = p.ProductID
            WHERE p.ProductID IS NULL;
        """)
        invalid_products = cursor.fetchone()[0]
        self.assertEqual(
            invalid_products,
            0,
            f"Found {invalid_products} order details with invalid ProductID"
        )
        
        conn.close()
    
    def test_sample_queries(self):
        """Run simple SELECT queries on each table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test simple SELECT on each table
        tables = ['Customers', 'Products', 'Employees', 'Orders', 'OrderDetails']
        for table in tables:
            cursor.execute(f"SELECT * FROM {table} LIMIT 1;")
            result = cursor.fetchone()
            self.assertIsNotNone(
                result,
                f"SELECT query on {table} returned no results"
            )
        
        # Test JOIN query
        cursor.execute("""
            SELECT o.OrderID, c.CompanyName, e.FirstName, e.LastName
            FROM Orders o
            JOIN Customers c ON o.CustomerID = c.CustomerID
            JOIN Employees e ON o.EmployeeID = e.EmployeeID
            LIMIT 5;
        """)
        results = cursor.fetchall()
        self.assertGreater(
            len(results),
            0,
            "JOIN query returned no results"
        )
        self.assertEqual(
            len(results[0]),
            4,
            "JOIN query did not return expected number of columns"
        )
        
        # Test aggregate query
        cursor.execute("""
            SELECT c.Country, COUNT(*) as OrderCount
            FROM Orders o
            JOIN Customers c ON o.CustomerID = c.CustomerID
            GROUP BY c.Country
            ORDER BY OrderCount DESC
            LIMIT 5;
        """)
        results = cursor.fetchall()
        self.assertGreater(
            len(results),
            0,
            "Aggregate query returned no results"
        )
        
        conn.close()


if __name__ == '__main__':
    unittest.main()

