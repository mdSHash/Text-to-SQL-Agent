"""
Tests for the complete LangGraph workflow.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os

from agent.graph import compiled_graph, run_agent, _route_after_execution, _route_after_error
from agent.state import AgentState


class TestGraphCompilation(unittest.TestCase):
    """Test graph compilation and structure."""
    
    def test_graph_compilation(self):
        """Test that the graph compiles without errors."""
        # The graph is already compiled in agent.graph
        self.assertIsNotNone(compiled_graph)
        
        # Verify it has the expected structure
        # LangGraph compiled graphs have a 'nodes' attribute
        self.assertTrue(hasattr(compiled_graph, 'invoke'))
    
    def test_routing_functions(self):
        """Test the routing functions work correctly."""
        # Test _route_after_execution with success
        state_success: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {"success": True},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        self.assertEqual(_route_after_execution(state_success), "formatter")
        
        # Test _route_after_execution with failure
        state_failure: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {"success": False},
            "error_message": "",
            "retry_count": 0,
            "final_answer": "",
            "trace": []
        }
        self.assertEqual(_route_after_execution(state_failure), "error_handler")
        
        # Test _route_after_error with retries available
        state_retry: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 2,
            "final_answer": "",
            "trace": []
        }
        self.assertEqual(_route_after_error(state_retry), "sql_generator")
        
        # Test _route_after_error with max retries
        state_max: AgentState = {
            "question": "",
            "schema": "",
            "sql_query": "",
            "sql_history": [],
            "validation_result": {},
            "execution_result": {},
            "error_message": "",
            "retry_count": 3,
            "final_answer": "",
            "trace": []
        }
        self.assertEqual(_route_after_error(state_max), "__end__")


class TestGraphWorkflow(unittest.TestCase):
    """Test the complete graph workflow."""
    
    @patch('agent.nodes.formatter.ChatGoogleGenerativeAI')
    @patch('agent.nodes.sql_generator.ChatGoogleGenerativeAI')
    def test_successful_query_flow(self, mock_gen_llm, mock_fmt_llm):
        """Test a successful query flow through the graph."""
        # Mock SQL generator
        mock_gen = Mock()
        mock_gen_response = Mock()
        mock_gen_response.content = "SELECT * FROM Customers LIMIT 5;"
        mock_gen.invoke.return_value = mock_gen_response
        mock_gen_llm.return_value = mock_gen
        
        # Mock formatter
        mock_fmt = Mock()
        mock_fmt_response = Mock()
        mock_fmt_response.content = "Here are 5 customers from the database."
        mock_fmt.invoke.return_value = mock_fmt_response
        mock_fmt_llm.return_value = mock_fmt
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = run_agent("Show me 5 customers")
        
        # Verify final state has final_answer
        self.assertIn("final_answer", result)
        self.assertGreater(len(result["final_answer"]), 0)
        
        # Verify no errors occurred
        self.assertEqual(result.get("retry_count", 0), 0)
        
        # Check trace has expected nodes
        trace_nodes = [entry["node"] for entry in result.get("trace", [])]
        self.assertIn("schema_loader", trace_nodes)
        self.assertIn("sql_generator", trace_nodes)
        self.assertIn("validator", trace_nodes)
        self.assertIn("executor", trace_nodes)
        self.assertIn("formatter", trace_nodes)
    
    @patch('agent.nodes.formatter.ChatGoogleGenerativeAI')
    @patch('agent.nodes.sql_generator.ChatGoogleGenerativeAI')
    def test_retry_flow(self, mock_gen_llm, mock_fmt_llm):
        """Test retry flow when SQL generation fails initially."""
        # Mock SQL generator to fail first, then succeed
        mock_gen = Mock()
        
        # First call returns invalid SQL, second call returns valid SQL
        mock_gen_response_1 = Mock()
        mock_gen_response_1.content = "SELECT * FROM NonExistentTable;"
        mock_gen_response_2 = Mock()
        mock_gen_response_2.content = "SELECT * FROM Customers LIMIT 3;"
        
        mock_gen.invoke.side_effect = [mock_gen_response_1, mock_gen_response_2]
        mock_gen_llm.return_value = mock_gen
        
        # Mock formatter
        mock_fmt = Mock()
        mock_fmt_response = Mock()
        mock_fmt_response.content = "Here are 3 customers."
        mock_fmt.invoke.return_value = mock_fmt_response
        mock_fmt_llm.return_value = mock_fmt
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = run_agent("Show me customers")
        
        # Verify retry occurred
        self.assertGreater(result.get("retry_count", 0), 0)
        
        # Verify final success
        self.assertIn("final_answer", result)
        self.assertGreater(len(result["final_answer"]), 0)
        
        # Check trace shows retry
        trace_nodes = [entry["node"] for entry in result.get("trace", [])]
        self.assertIn("error_handler", trace_nodes)
        
        # SQL generator should appear twice (initial + retry)
        sql_gen_count = trace_nodes.count("sql_generator")
        self.assertGreaterEqual(sql_gen_count, 2)
    
    @patch('agent.nodes.sql_generator.ChatGoogleGenerativeAI')
    def test_max_retries(self, mock_gen_llm):
        """Test that the graph stops after max retries."""
        # Mock SQL generator to always return invalid SQL
        mock_gen = Mock()
        mock_gen_response = Mock()
        mock_gen_response.content = "SELECT * FROM NonExistentTable;"
        mock_gen.invoke.return_value = mock_gen_response
        mock_gen_llm.return_value = mock_gen
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = run_agent("Show me data")
        
        # Verify it stopped after 3 retries
        self.assertEqual(result.get("retry_count", 0), 3)
        
        # Check final_answer contains error message
        self.assertIn("final_answer", result)
        self.assertIn("Failed to generate valid SQL", result["final_answer"])
        
        # Verify trace shows all retry attempts
        trace_nodes = [entry["node"] for entry in result.get("trace", [])]
        error_handler_count = trace_nodes.count("error_handler")
        self.assertEqual(error_handler_count, 3)


class TestGraphEdgeCases(unittest.TestCase):
    """Test edge cases in the graph workflow."""
    
    @patch('agent.nodes.sql_generator.ChatGoogleGenerativeAI')
    def test_empty_question(self, mock_gen_llm):
        """Test graph handles empty question."""
        mock_gen = Mock()
        mock_gen_response = Mock()
        mock_gen_response.content = "SELECT 1;"
        mock_gen.invoke.return_value = mock_gen_response
        mock_gen_llm.return_value = mock_gen
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = run_agent("")
        
        # Should still complete
        self.assertIn("final_answer", result)
    
    def test_graph_without_api_key(self):
        """Test graph handles missing API key gracefully."""
        with patch.dict('os.environ', {}, clear=True):
            result = run_agent("Show me customers")
        
        # Should have error in trace or final_answer
        self.assertTrue(
            len(result.get("error_message", "")) > 0 or
            "error" in result.get("final_answer", "").lower()
        )


if __name__ == '__main__':
    unittest.main()

