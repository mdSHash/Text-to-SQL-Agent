"""
SQL validator node for the LangGraph text-to-SQL agent.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from agent.state import AgentState

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "northwind.db"


def validate_sql(state: AgentState) -> AgentState:
    """Validate the generated SQL using SQLite query planning."""
    trace = state.setdefault("trace", [])
    sql_query = state.get("sql_query", "").strip()

    if not sql_query:
        state["validation_result"] = {
            "valid": False,
            "message": "No SQL query available for validation.",
        }
        trace.append(
            {
                "node": "validator",
                "timestamp": datetime.utcnow().isoformat(),
                "details": state["validation_result"],
            }
        )
        return state

    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute(f"EXPLAIN QUERY PLAN {sql_query}")
            cursor.fetchall()

        state["validation_result"] = {
            "valid": True,
            "message": "SQL query passed EXPLAIN QUERY PLAN validation.",
        }
        trace.append(
            {
                "node": "validator",
                "timestamp": datetime.utcnow().isoformat(),
                "details": state["validation_result"],
            }
        )
    except sqlite3.Error as exc:
        message = f"SQL validation failed: {exc}"
        state["validation_result"] = {
            "valid": False,
            "message": message,
        }
        state["error_message"] = message
        trace.append(
            {
                "node": "validator",
                "timestamp": datetime.utcnow().isoformat(),
                "details": state["validation_result"],
            }
        )
    except Exception as exc:
        message = f"Unexpected validator error: {exc}"
        state["validation_result"] = {
            "valid": False,
            "message": message,
        }
        state["error_message"] = message
        trace.append(
            {
                "node": "validator",
                "timestamp": datetime.utcnow().isoformat(),
                "details": state["validation_result"],
            }
        )

    return state

