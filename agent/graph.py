"""
LangGraph workflow definition for the text-to-SQL agent.
"""

from __future__ import annotations

from datetime import datetime

from langgraph.graph import END, START, StateGraph

from agent.nodes.error_handler import handle_error
from agent.nodes.executor import execute_sql
from agent.nodes.formatter import format_answer
from agent.nodes.schema_loader import load_schema
from agent.nodes.sql_generator import generate_sql
from agent.nodes.validator import validate_sql
from agent.state import AgentState


def _route_after_execution(state: AgentState) -> str:
    """Route to formatter on success or error handler on failure."""
    execution_result = state.get("execution_result", {})
    return "formatter" if execution_result.get("success") is True else "error_handler"


def _route_after_error(state: AgentState) -> str:
    """Route back to SQL generation for retry or end after max retries."""
    return "sql_generator" if state.get("retry_count", 0) < 3 else END


graph_builder = StateGraph(AgentState)

graph_builder.add_node("schema_loader", load_schema)
graph_builder.add_node("sql_generator", generate_sql)
graph_builder.add_node("validator", validate_sql)
graph_builder.add_node("executor", execute_sql)
graph_builder.add_node("error_handler", handle_error)
graph_builder.add_node("formatter", format_answer)

graph_builder.add_edge(START, "schema_loader")
graph_builder.add_edge("schema_loader", "sql_generator")
graph_builder.add_edge("sql_generator", "validator")
graph_builder.add_edge("validator", "executor")
graph_builder.add_conditional_edges(
    "executor",
    _route_after_execution,
    {
        "formatter": "formatter",
        "error_handler": "error_handler",
    },
)
graph_builder.add_conditional_edges(
    "error_handler",
    _route_after_error,
    {
        "sql_generator": "sql_generator",
        END: END,
    },
)
graph_builder.add_edge("formatter", END)

compiled_graph = graph_builder.compile()


def run_agent(question: str) -> dict:
    """Run the LangGraph text-to-SQL workflow for a user question."""
    initial_state: AgentState = {
        "question": question,
        "schema": "",
        "sql_query": "",
        "sql_history": [],
        "validation_result": {},
        "execution_result": {},
        "error_message": "",
        "retry_count": 0,
        "final_answer": "",
        "trace": [
            {
                "node": "run_agent",
                "timestamp": datetime.utcnow().isoformat(),
                "details": f"Initialized agent for question: {question}",
            }
        ],
    }

    final_state = compiled_graph.invoke(initial_state)
    return dict(final_state)

