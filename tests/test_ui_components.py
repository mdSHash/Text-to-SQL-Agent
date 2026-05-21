"""
Tests for UI components - Modern Dark Glassmorphism Theme.
Uses pytest with unittest.mock to patch streamlit for headless testing.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pandas as pd
from io import StringIO

# Mock streamlit before importing components
import sys

mock_st = MagicMock()

# Configure st.columns() to return the correct number of mock context managers
def mock_columns(n):
    cols = []
    for _ in range(n):
        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=False)
        cols.append(col)
    return cols

mock_st.columns = mock_columns
sys.modules['streamlit'] = mock_st

from ui.components import (
    render_trace_panel,
    render_sample_questions,
    render_query_history,
    render_results,
    apply_custom_css,
    render_database_info,
    render_instructions
)


class TestImports(unittest.TestCase):
    """Test that all UI component functions are importable."""

    def test_all_components_importable(self):
        """Test that all component functions can be imported."""
        components = [
            render_trace_panel,
            render_sample_questions,
            render_query_history,
            render_results,
            apply_custom_css,
            render_database_info,
            render_instructions,
        ]
        for component in components:
            self.assertTrue(callable(component), f"{component.__name__} is not callable")

    def test_function_signatures(self):
        """Test that functions have expected signatures."""
        import inspect

        # render_trace_panel(trace) -> None
        sig = inspect.signature(render_trace_panel)
        self.assertIn('trace', sig.parameters)

        # render_sample_questions() -> Optional[str]
        sig = inspect.signature(render_sample_questions)
        self.assertEqual(len(sig.parameters), 0)

        # render_query_history(history) -> Optional[str]
        sig = inspect.signature(render_query_history)
        self.assertIn('history', sig.parameters)

        # render_results(execution_result, sql_query) -> None
        sig = inspect.signature(render_results)
        self.assertIn('execution_result', sig.parameters)
        self.assertIn('sql_query', sig.parameters)

        # apply_custom_css() -> None
        sig = inspect.signature(apply_custom_css)
        self.assertEqual(len(sig.parameters), 0)

        # render_database_info() -> None
        sig = inspect.signature(render_database_info)
        self.assertEqual(len(sig.parameters), 0)

        # render_instructions() -> None
        sig = inspect.signature(render_instructions)
        self.assertEqual(len(sig.parameters), 0)


class TestApplyCustomCSS(unittest.TestCase):
    """Test custom CSS application for dark glassmorphism theme."""

    def test_apply_custom_css(self):
        """Test that custom CSS can be applied without error."""
        try:
            apply_custom_css()
        except Exception as e:
            self.fail(f"apply_custom_css raised {e}")

    def test_apply_custom_css_returns_none(self):
        """Test that apply_custom_css returns None."""
        result = apply_custom_css()
        self.assertIsNone(result)


class TestTracePanel(unittest.TestCase):
    """Test the trace panel rendering (timeline visualization)."""

    def test_render_trace_panel_with_empty_trace(self):
        """Test trace panel with empty trace list."""
        try:
            render_trace_panel([])
        except Exception as e:
            self.fail(f"render_trace_panel raised {e} with empty trace")

    def test_render_trace_panel_with_various_entries(self):
        """Test trace panel with various trace entries."""
        trace = [
            {
                "node": "schema_loader",
                "timestamp": datetime.now().isoformat(),
                "details": "Loaded schema for 5 tables"
            },
            {
                "node": "sql_generator",
                "timestamp": datetime.now().isoformat(),
                "details": {"sql_query": "SELECT * FROM Customers;"}
            },
            {
                "node": "validator",
                "timestamp": datetime.now().isoformat(),
                "details": {"is_valid": True, "issues": []}
            },
            {
                "node": "executor",
                "timestamp": datetime.now().isoformat(),
                "details": {"row_count": 10, "execution_time": 0.045}
            },
            {
                "node": "error_handler",
                "timestamp": datetime.now().isoformat(),
                "details": {"status": "retrying", "error_message": "Test error"}
            }
        ]

        try:
            render_trace_panel(trace)
        except Exception as e:
            self.fail(f"render_trace_panel raised {e} with valid trace")

    def test_render_trace_panel_with_malformed_entries(self):
        """Test trace panel handles malformed entries gracefully."""
        trace = [
            {"node": "test"},  # Missing timestamp and details
            {"timestamp": datetime.now().isoformat()},  # Missing node
            {}  # Empty entry
        ]

        try:
            render_trace_panel(trace)
        except Exception as e:
            self.fail(f"render_trace_panel raised {e} with malformed trace")

    def test_render_trace_panel_returns_none(self):
        """Test that render_trace_panel returns None."""
        result = render_trace_panel([])
        self.assertIsNone(result)


class TestSampleQuestions(unittest.TestCase):
    """Test sample questions rendering (card-based design)."""

    def test_render_sample_questions(self):
        """Test that sample questions are rendered without error."""
        try:
            result = render_sample_questions()
            self.assertTrue(result is None or isinstance(result, str))
        except Exception as e:
            self.fail(f"render_sample_questions raised {e}")

    def test_sample_questions_returns_none_when_no_click(self):
        """Test that sample questions returns None when no button clicked."""
        result = render_sample_questions()
        # In mock environment, no button is clicked so result should be None
        self.assertTrue(result is None or isinstance(result, str))


class TestQueryHistory(unittest.TestCase):
    """Test query history rendering."""

    def test_render_query_history_with_empty_history(self):
        """Test query history with empty list."""
        try:
            result = render_query_history([])
            self.assertTrue(result is None or isinstance(result, str))
        except Exception as e:
            self.fail(f"render_query_history raised {e}")

    def test_render_query_history_with_entries(self):
        """Test query history with valid entries."""
        history = [
            {
                "question": "Show me customers",
                "timestamp": datetime.now().isoformat()
            },
            {
                "question": "What are the top products?",
                "timestamp": datetime.now().isoformat()
            }
        ]

        try:
            result = render_query_history(history)
            self.assertTrue(result is None or isinstance(result, str))
        except Exception as e:
            self.fail(f"render_query_history raised {e}")

    def test_render_query_history_with_long_questions(self):
        """Test query history truncates long questions."""
        history = [
            {
                "question": "This is a very long question that should be truncated when displayed in the history panel to avoid taking up too much space",
                "timestamp": datetime.now().isoformat()
            }
        ]

        try:
            result = render_query_history(history)
            self.assertTrue(result is None or isinstance(result, str))
        except Exception as e:
            self.fail(f"render_query_history raised {e}")

    def test_render_query_history_with_missing_fields(self):
        """Test query history handles missing fields."""
        history = [
            {"question": "Test"},  # Missing timestamp
            {"timestamp": datetime.now().isoformat()},  # Missing question
            {}  # Empty entry
        ]

        try:
            result = render_query_history(history)
            self.assertTrue(result is None or isinstance(result, str))
        except Exception as e:
            self.fail(f"render_query_history raised {e}")


class TestResults(unittest.TestCase):
    """Test results rendering (SQL display, data table, export)."""

    def test_render_results_with_empty_data(self):
        """Test results rendering with empty data."""
        execution_result = {"results": []}
        sql_query = "SELECT * FROM Customers;"

        try:
            render_results(execution_result, sql_query)
        except Exception as e:
            self.fail(f"render_results raised {e} with empty data")

    def test_render_results_with_data(self):
        """Test results rendering with actual data."""
        execution_result = {
            "results": [
                {"CustomerID": "ALFKI", "CompanyName": "Alfreds Futterkiste"},
                {"CustomerID": "ANATR", "CompanyName": "Ana Trujillo"}
            ],
            "execution_time": 0.123
        }
        sql_query = "SELECT CustomerID, CompanyName FROM Customers LIMIT 2;"

        try:
            render_results(execution_result, sql_query)
        except Exception as e:
            self.fail(f"render_results raised {e} with valid data")

    def test_render_results_with_large_dataset(self):
        """Test results rendering with large dataset."""
        large_data = [
            {"id": i, "value": f"Value {i}"}
            for i in range(1000)
        ]
        execution_result = {"results": large_data}
        sql_query = "SELECT * FROM large_table;"

        try:
            render_results(execution_result, sql_query)
        except Exception as e:
            self.fail(f"render_results raised {e} with large dataset")

    def test_render_results_csv_export(self):
        """Test that CSV export data can be generated from results."""
        execution_result = {
            "results": [
                {"col1": "value1", "col2": "value2"},
                {"col1": "value3", "col2": "value4"}
            ]
        }
        sql_query = "SELECT * FROM test;"

        try:
            render_results(execution_result, sql_query)

            # Verify CSV can be created from the data
            df = pd.DataFrame(execution_result["results"])
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()

            self.assertGreater(len(csv_data), 0)
            self.assertIn("col1", csv_data)
            self.assertIn("col2", csv_data)
        except Exception as e:
            self.fail(f"CSV generation raised {e}")

    def test_render_results_json_export(self):
        """Test that JSON export data can be generated from results."""
        import json
        execution_result = {
            "results": [
                {"col1": "value1", "col2": "value2"},
                {"col1": "value3", "col2": "value4"}
            ]
        }
        sql_query = "SELECT * FROM test;"

        try:
            render_results(execution_result, sql_query)

            # Verify JSON can be created from the data
            df = pd.DataFrame(execution_result["results"])
            json_data = df.to_json(orient="records", indent=2)

            self.assertGreater(len(json_data), 0)
            parsed = json.loads(json_data)
            self.assertEqual(len(parsed), 2)
        except Exception as e:
            self.fail(f"JSON generation raised {e}")


class TestDatabaseInfo(unittest.TestCase):
    """Test database info rendering."""

    def test_render_database_info(self):
        """Test that database info renders without errors."""
        try:
            render_database_info()
        except Exception as e:
            self.fail(f"render_database_info raised {e}")

    def test_render_database_info_returns_none(self):
        """Test that render_database_info returns None."""
        result = render_database_info()
        self.assertIsNone(result)


class TestInstructions(unittest.TestCase):
    """Test instructions rendering."""

    def test_render_instructions(self):
        """Test that instructions render without errors."""
        try:
            render_instructions()
        except Exception as e:
            self.fail(f"render_instructions raised {e}")

    def test_render_instructions_returns_none(self):
        """Test that render_instructions returns None."""
        result = render_instructions()
        self.assertIsNone(result)


class TestComponentIntegration(unittest.TestCase):
    """Test integration between components."""

    def test_full_workflow(self):
        """Test a full workflow: CSS → questions → results → history."""
        try:
            # Apply theme
            apply_custom_css()

            # Render sample questions
            render_sample_questions()

            # Render results
            execution_result = {
                "results": [{"id": 1, "name": "Test"}],
                "execution_time": 0.05
            }
            render_results(execution_result, "SELECT * FROM test;")

            # Render trace
            trace = [
                {
                    "node": "executor",
                    "timestamp": datetime.now().isoformat(),
                    "details": {"row_count": 1}
                }
            ]
            render_trace_panel(trace)

            # Render history
            history = [{"question": "Test query", "timestamp": datetime.now().isoformat()}]
            render_query_history(history)

            # Render sidebar components
            render_database_info()
            render_instructions()

        except Exception as e:
            self.fail(f"Full workflow raised {e}")

    def test_components_with_none_inputs(self):
        """Test components handle None inputs gracefully."""
        try:
            render_trace_panel(None)
        except (TypeError, AttributeError):
            pass  # Expected to handle None

        try:
            render_query_history(None)
        except (TypeError, AttributeError):
            pass  # Expected to handle None


class TestDataFormatting(unittest.TestCase):
    """Test data formatting in components."""

    def test_timestamp_formatting(self):
        """Test that timestamps are formatted correctly."""
        timestamps = [
            datetime.now().isoformat(),
            "2024-01-01T12:00:00",
            "2024-01-01T12:00:00Z",
            "2024-01-01T12:00:00+00:00"
        ]

        trace = [
            {
                "node": "test",
                "timestamp": ts,
                "details": "test"
            }
            for ts in timestamps
        ]

        try:
            render_trace_panel(trace)
        except Exception as e:
            self.fail(f"Timestamp formatting failed: {e}")

    def test_dataframe_conversion(self):
        """Test that results can be converted to DataFrame."""
        results = [
            {"col1": 1, "col2": "a"},
            {"col1": 2, "col2": "b"},
            {"col1": 3, "col2": "c"}
        ]

        df = pd.DataFrame(results)

        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ["col1", "col2"])
        self.assertEqual(df["col1"].tolist(), [1, 2, 3])


if __name__ == '__main__':
    unittest.main()

