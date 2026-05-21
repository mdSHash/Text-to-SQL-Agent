"""
Tests for individual agent nodes.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sqlite3
import tempfile
import shutil

from agent.state import AgentState
from agent.nodes.schema_loader import load_schema
from agent.nodes.sql_generator import generate_sql
from agent.nodes.validator import validate_sql
from agent.nodes.executor import execute_sql
from agent.nodes.error_handler import handle_error
from agent.nodes.formatter import format_answer


class TestSchemaLoader(unittest.TestCase):
    """Test the schema loader node."""
    
    def test_schema_loader(self):
        """Test that schema loader populates state correctly."""
        # Create minimal state
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        # Call load_schema node
        result = load_schema(state)
        
        # Verify schema is populated
        self.assertIsNotNone(result["schema"])
        self.assertGreater(len(result["schema"]), 0, "Schema should not be empty")
        
        # Check schema contains table information
        self.assertIn("Table:", result["schema"])
        self.assertIn("Columns:", result["schema"])
        
        # Verify at least one expected table is present
        expected_tables = ["Customers", "Products", "Employees", "Orders", "OrderDetails"]
        schema_has_table = any(table in result["schema"] for table in expected_tables)
        self.assertTrue(schema_has_table, "Schema should contain at least one expected table")
        
        # Verify trace entry was added
        self.assertGreater(len(result["trace"]), 0)
        self.assertEqual(result["trace"][0]["node"], "schema_loader")
        self.assertIn("details", result["trace"][0])
    
    def test_schema_loader_with_missing_database(self):
        """Test schema loader handles missing database gracefully."""
        # Temporarily patch DB_PATH to non-existent file
        with patch('agent.nodes.schema_loader.DB_PATH', Path('nonexistent.db')):
            state: AgentState = {
                "question": "",
                "schema": "",
                "sql_query": "",
                "sql_history": [],
                "validation_result": {},
                "execution_result": {},
                "error_message": "",
                "retry_count": 0,
                "final_answer": "",
                "trace": []
            }
            
            result = load_schema(state)
            
            # Should have error message
            self.assertIn("error_message", result)
            self.assertGreater(len(result["error_message"]), 0)
            
            # Schema should be empty
            self.assertEqual(result["schema"], "")


class TestSQLGenerator(unittest.TestCase):
    """Test the SQL generator node."""
    
    @patch('agent.nodes.sql_generator.ChatGoogleGenerativeAI')
    def test_sql_generator(self, mock_llm_class):
        """Test SQL generator with mocked Gemini API."""
        # Mock the LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "SELECT * FROM Customers LIMIT 10;"
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        # Create state with schema and question
        state: AgentState = {
            "question": "Show me 10 customers",
            "schema": "Table: Customers\nColumns: CustomerID, CompanyName",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        # Mock environment variable
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = generate_sql(state)
        
        # Verify SQL query is generated
        self.assertIsNotNone(result["sql_query"])
        self.assertGreater(len(result["sql_query"]), 0)
        self.assertIn("SELECT", result["sql_query"])
        
        # Check sql_history is updated
        self.assertEqual(len(result["sql_history"]), 1)
        self.assertEqual(result["sql_history"][0], result["sql_query"])
        
        # Verify trace entry was added
        self.assertGreater(len(result["trace"]), 0)
        self.assertEqual(result["trace"][0]["node"], "sql_generator")
    
    @patch('agent.nodes.sql_generator.ChatGoogleGenerativeAI')
    def test_sql_generator_strips_markdown(self, mock_llm_class):
        """Test that SQL generator strips markdown code blocks."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "```sql\nSELECT * FROM Products;\n```"
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        state: AgentState = {
            "question": "Show products",
            "schema": "Table: Products\nColumns: ProductID, ProductName",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = generate_sql(state)
        
        # Should not contain markdown
        self.assertNotIn("```", result["sql_query"])
        self.assertIn("SELECT", result["sql_query"])
    
    def test_sql_generator_without_api_key(self):
        """Test SQL generator handles missing API key."""
        state: AgentState = {
            "question": "Show customers",
            "schema": "Table: Customers",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        with patch.dict('os.environ', {}, clear=True):
            result = generate_sql(state)
        
        # Should have error
        self.assertIn("error_message", result)
        self.assertIn("GOOGLE_API_KEY", result["error_message"])


class TestValidator(unittest.TestCase):
    """Test the SQL validator node."""
    
    def test_validator_with_valid_sql(self):
        """Test validator with valid SQL query."""
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "SELECT * FROM Customers LIMIT 5;",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        result = validate_sql(state)
        
        # Verify validation_result is populated
        self.assertIn("validation_result", result)
        self.assertIn("valid", result["validation_result"])
        self.assertTrue(result["validation_result"]["valid"])
        
        # Verify trace entry was added
        self.assertGreater(len(result["trace"]), 0)
        self.assertEqual(result["trace"][0]["node"], "validator")
    
    def test_validator_with_invalid_sql(self):
        """Test validator with invalid SQL and check error handling."""
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "SELECT * FROM NonExistentTable;",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        result = validate_sql(state)
        
        # Should be invalid
        self.assertFalse(result["validation_result"]["valid"])
        self.assertIn("error_message", result)
        self.assertGreater(len(result["error_message"]), 0)
    
    def test_validator_with_empty_query(self):
        """Test validator with empty SQL query."""
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        result = validate_sql(state)
        
        # Should be invalid
        self.assertFalse(result["validation_result"]["valid"])
        self.assertIn("No SQL query", result["validation_result"]["message"])


class TestExecutor(unittest.TestCase):
    """Test the SQL executor node."""
    
    def test_executor_with_valid_sql(self):
        """Test executor with valid SQL query."""
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "SELECT * FROM Customers LIMIT 3;",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        result = execute_sql(state)
        
        # Verify execution_result contains data
        self.assertIn("execution_result", result)
        self.assertTrue(result["execution_result"]["success"])
        self.assertIn("data", result["execution_result"])
        self.assertIn("columns", result["execution_result"])
        
        # Should have data
        self.assertGreater(len(result["execution_result"]["data"]), 0)
        self.assertGreater(len(result["execution_result"]["columns"]), 0)
        
        # Error message should be cleared
        self.assertEqual(result["error_message"], "")
    
    def test_executor_with_invalid_sql(self):
        """Test executor with invalid SQL and check error handling."""
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "SELECT * FROM NonExistentTable;",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        result = execute_sql(state)
        
        # Should fail
        self.assertFalse(result["execution_result"]["success"])
        self.assertIn("error", result["execution_result"])
        
        # Verify retry_count increments on error
        self.assertEqual(result["retry_count"], 1)
        self.assertGreater(len(result["error_message"]), 0)
    
    def test_executor_with_empty_query(self):
        """Test executor with empty SQL query."""
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        result = execute_sql(state)
        
        # Should fail
        self.assertFalse(result["execution_result"]["success"])
        self.assertEqual(result["retry_count"], 1)


class TestErrorHandler(unittest.TestCase):
    """Test the error handler node."""
    
    def test_error_handler_with_retries_available(self):
        """Test error handler when retry_count < 3."""
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "Some error occurred",
            "retry_count": 1,
            "final_answer": "",
            "trace": []
        }
        
        result = handle_error(state)
        
        # Verify trace entry added
        self.assertGreater(len(result["trace"]), 0)
        self.assertEqual(result["trace"][0]["node"], "error_handler")
        self.assertEqual(result["trace"][0]["details"]["status"], "retrying")
        
        # final_answer should not be set yet
        self.assertEqual(result.get("final_answer", ""), "")
    
    def test_error_handler_max_retries_reached(self):
        """Test error handler when retry_count >= 3."""
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "Persistent error",
            "retry_count": 3,
            "final_answer": "",
            "trace": []
        }
        
        result = handle_error(state)
        
        # Verify final_answer is set when max retries reached
        self.assertIn("final_answer", result)
        self.assertGreater(len(result["final_answer"]), 0)
        self.assertIn("Failed to generate valid SQL", result["final_answer"])
        self.assertIn("Persistent error", result["final_answer"])
        
        # Verify trace
        self.assertEqual(result["trace"][0]["details"]["status"], "max_retries_reached")


class TestFormatter(unittest.TestCase):
    """Test the answer formatter node."""
    
    @patch('agent.nodes.formatter.ChatGoogleGenerativeAI')
    def test_formatter(self, mock_llm_class):
        """Test formatter with mocked Gemini API."""
        # Mock the LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Based on the query results, there are 3 customers in the database."
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        # Create state with successful execution results
        state: AgentState = {
            "question": "How many customers are there?",
            "schema": "",
            "sql_query": "SELECT COUNT(*) FROM Customers;",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {
                "success": True,
                "data": [[91]],
                "columns": ["COUNT(*)"]
            },
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = format_answer(state)
        
        # Verify final_answer is populated
        self.assertIn("final_answer", result)
        self.assertGreater(len(result["final_answer"]), 0)
        
        # Check trace entry was added
        self.assertGreater(len(result["trace"]), 0)
        self.assertEqual(result["trace"][0]["node"], "formatter")
    
    def test_formatter_without_api_key(self):
        """Test formatter handles missing API key."""
        state: AgentState = {
            "question": "Test question",
            "schema": "",
            "sql_query": "SELECT * FROM Customers;",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {
                "success": True,
                "data": [["ALFKI", "Alfreds Futterkiste"]],
                "columns": ["CustomerID", "CompanyName"]
            },
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        with patch.dict('os.environ', {}, clear=True):
            result = format_answer(state)
        
        # Should have final_answer with error
        self.assertIn("final_answer", result)
        self.assertIn("formatting the final answer failed", result["final_answer"])


if __name__ == '__main__':
    unittest.main()

