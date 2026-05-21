"""
Error handler node for the LangGraph text-to-SQL agent.
"""

from __future__ import annotations

from datetime import datetime

from agent.state import AgentState


def handle_error(state: AgentState) -> AgentState:
    """Handle execution errors and determine whether retries should continue."""
    trace = state.setdefault("trace", [])
    retry_count = state.get("retry_count", 0)
    error_message = state.get("error_message", "Unknown error.")

    if retry_count >= 3:
        state["final_answer"] = (
            "Failed to generate valid SQL after 3 attempts. "
            f"Last error: {error_message}"
        )
        trace.append(
            {
                "node": "error_handler",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "status": "max_retries_reached",
                    "retry_count": retry_count,
                    "error_message": error_message,
                },
            }
        )
    else:
        trace.append(
            {
                "node": "error_handler",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "status": "retrying",
                    "retry_count": retry_count,
                    "error_message": error_message,
                },
            }
        )

    return state

