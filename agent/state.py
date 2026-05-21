"""
Agent state definition for the LangGraph text-to-SQL workflow.
"""

from typing import Any, Dict, List, TypedDict


class AgentState(TypedDict):
    """Typed state shared across all LangGraph nodes."""

    question: str
    schema: str
    sql_query: str
    sql_history: List[str]
    validation_result: Dict[str, Any]
    execution_result: Dict[str, Any]
    error_message: str
    retry_count: int
    final_answer: str
    trace: List[Dict[str, Any]]

