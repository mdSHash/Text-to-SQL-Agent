"""
End-to-end integration tests for the nl2sql-agent system.
"""

import unittest
import os
from pathlib import Path
import tempfile
import shutil

from agent.graph import run_agent


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.has_api_key = os.getenv("GOOGLE_API_KEY") is not None
        cls.db_path = Path("data/northwind.db")
    
    @unittest.skipIf(not os.getenv("GOOGLE_API_KEY"), "GOOGLE_API_KEY not set")
    def test_end_to_end_query(self):
        """Run the complete agent with a simple question."""
        question = "How many customers are in the database?"
        
        result = run_agent(question)
        
        # Verify final_answer is generated
        self.assertIn("final_answer", result)
        self.assertGreater(len(result["final_answer"]), 0)
        
        # Check trace has all expected nodes
        trace_nodes = [entry["node"] for entry in result.get("trace", [])]
        expected_nodes = ["schema_loader", "sql_generator", "validator", "executor"]
        for node in expected_nodes:
            self.assertIn(node, trace_nodes, f"Expected node {node} not found in trace")
        
        # Verify SQL was generated and executed
        self.assertIn("sql_query", result)
        self.assertGreater(len(result["sql_query"]), 0)
        
        # Verify execution was successful
        self.assertIn("execution_result", result)
        self.assertTrue(result["execution_result"].get("success", False))
    
    @unittest.skipIf(not os.getenv("GOOGLE_API_KEY"), "GOOGLE_API_KEY not set")
    def test_multiple_queries(self):
        """Run multiple different sample questions."""
        questions = [
            "List 5 products from the database",
            "Show me all employees",
            "What countries do our customers come from?"
        ]
        
        results = []
        for question in questions:
            result = run_agent(question)
            results.append(result)
            
            # Verify each completes successfully
            self.assertIn("final_answer", result)
            self.assertGreater(len(result["final_answer"]), 0)
        
        # Check results are different for different questions
        final_answers = [r["final_answer"] for r in results]
        # At least some answers should be different
        unique_answers = set(final_answers)
        self.assertGreater(len(unique_answers), 1, "All answers are identical")
        
        # Verify trace is unique for each query
        for result in results:
            trace = result.get("trace", [])
            self.assertGreater(len(trace), 0)
    
    def test_database_connection_error(self):
        """Test that database connection errors are handled gracefully."""
        # Create a temporary backup of the database
        if self.db_path.exists():
            backup_path = self.db_path.with_suffix('.db.backup')
            shutil.copy(self.db_path, backup_path)
            temp_path = self.db_path.with_suffix('.db.temp')
            
            try:
                # Temporarily rename the database file
                self.db_path.rename(temp_path)
                
                # Run a query - should handle error gracefully
                result = run_agent("Show me customers")
                
                # Should have error information
                self.assertTrue(
                    len(result.get("error_message", "")) > 0 or
                    "error" in result.get("final_answer", "").lower() or
                    result.get("retry_count", 0) > 0
                )
                
            finally:
                # Restore database file
                if temp_path.exists():
                    temp_path.rename(self.db_path)
                if backup_path.exists():
                    backup_path.unlink()
        else:
            self.skipTest("Database file not found")


class TestIntegrationWithoutAPIKey(unittest.TestCase):
    """Integration tests that don't require API key."""
    
    def test_schema_loading_without_api_key(self):
        """Test that schema loading works without API key."""
        from agent.nodes.schema_loader import load_schema
        from agent.state import AgentState
        
        state: AgentState = {
            "question": "Test",
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
        
        # Schema should be loaded regardless of API key
        self.assertGreater(len(result["schema"]), 0)
        self.assertIn("Table:", result["schema"])
    
    def test_sql_validation_without_api_key(self):
        """Test that SQL validation works without API key."""
        from agent.nodes.validator import validate_sql
        from agent.state import AgentState
        
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
        
        # Validation should work without API key
        self.assertIn("validation_result", result)
        self.assertTrue(result["validation_result"]["valid"])
    
    def test_sql_execution_without_api_key(self):
        """Test that SQL execution works without API key."""
        from agent.nodes.executor import execute_sql
        from agent.state import AgentState
        
        state: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "SELECT COUNT(*) as total FROM Customers;",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        result = execute_sql(state)
        
        # Execution should work without API key
        self.assertTrue(result["execution_result"]["success"])
        self.assertGreater(len(result["execution_result"]["data"]), 0)


class TestComplexQueries(unittest.TestCase):
    """Test complex query scenarios."""
    
    @unittest.skipIf(not os.getenv("GOOGLE_API_KEY"), "GOOGLE_API_KEY not set")
    def test_aggregation_query(self):
        """Test query with aggregation."""
        question = "What is the total number of orders?"
        result = run_agent(question)
        
        self.assertIn("final_answer", result)
        self.assertIn("sql_query", result)
        # Should contain COUNT or similar aggregation
        self.assertTrue(
            "COUNT" in result["sql_query"].upper() or
            "SUM" in result["sql_query"].upper()
        )
    
    @unittest.skipIf(not os.getenv("GOOGLE_API_KEY"), "GOOGLE_API_KEY not set")
    def test_join_query(self):
        """Test query requiring joins."""
        question = "Show me orders with customer names"
        result = run_agent(question)
        
        self.assertIn("final_answer", result)
        self.assertIn("sql_query", result)
        # Should contain JOIN
        self.assertIn("JOIN", result["sql_query"].upper())
    
    @unittest.skipIf(not os.getenv("GOOGLE_API_KEY"), "GOOGLE_API_KEY not set")
    def test_filtering_query(self):
        """Test query with filtering."""
        question = "Show me customers from USA"
        result = run_agent(question)
        
        self.assertIn("final_answer", result)
        self.assertIn("sql_query", result)
        # Should contain WHERE clause
        self.assertIn("WHERE", result["sql_query"].upper())


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery mechanisms."""
    
    def test_invalid_sql_recovery(self):
        """Test that system can recover from invalid SQL."""
        from agent.nodes.executor import execute_sql
        from agent.nodes.error_handler import handle_error
        from agent.state import AgentState
        
        # Start with invalid SQL
        state: AgentState = {
            "question": "Test",
            "schema": "",
            "sql_query": "INVALID SQL QUERY",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        
        # Execute (should fail)
        state = execute_sql(state)
        self.assertFalse(state["execution_result"]["success"])
        self.assertEqual(state["retry_count"], 1)
        
        # Handle error
        state = handle_error(state)
        self.assertGreater(len(state["trace"]), 0)
        
        # Should allow retry
        self.assertLess(state["retry_count"], 3)
    
    def test_max_retry_handling(self):
        """Test that max retries are properly enforced."""
        from agent.nodes.error_handler import handle_error
        from agent.state import AgentState
        
        state: AgentState = {
            "question": "Test",
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
        
        state = handle_error(state)
        
        # Should set final_answer with error
        self.assertIn("final_answer", state)
        self.assertIn("Failed to generate valid SQL", state["final_answer"])


if __name__ == '__main__':
    unittest.main()

