"""
SQL executor node for the LangGraph text-to-SQL agent.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, List

from agent.state import AgentState

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "northwind.db"


def _serialize_rows(rows: List[tuple[Any, ...]]) -> List[List[Any]]:
    """Convert SQLite row tuples into JSON-serializable lists."""
    return [list(row) for row in rows]


def execute_sql(state: AgentState) -> AgentState:
    """Execute the generated SQL query and store result metadata in state."""
    trace = state.setdefault("trace", [])
    sql_query = state.get("sql_query", "").strip()

    if not sql_query:
        message = "No SQL query available for execution."
        state["execution_result"] = {"success": False, "error": message}
        state["error_message"] = message
        state["retry_count"] = state.get("retry_count", 0) + 1
        trace.append(
            {
                "node": "executor",
                "timestamp": datetime.utcnow().isoformat(),
                "details": state["execution_result"],
            }
        )
        return state

    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description or []]

        state["execution_result"] = {
            "success": True,
            "data": _serialize_rows(rows),
            "columns": column_names,
        }
        state["error_message"] = ""
        trace.append(
            {
                "node": "executor",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "success": True,
                    "row_count": len(rows),
                    "columns": column_names,
                },
            }
        )
    except sqlite3.Error as exc:
        message = f"SQL execution failed: {exc}"
        state["execution_result"] = {"success": False, "error": message}
        state["error_message"] = message
        state["retry_count"] = state.get("retry_count", 0) + 1
        trace.append(
            {
                "node": "executor",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "success": False,
                    "error": message,
                    "retry_count": state["retry_count"],
                },
            }
        )
    except Exception as exc:
        message = f"Unexpected executor error: {exc}"
        state["execution_result"] = {"success": False, "error": message}
        state["error_message"] = message
        state["retry_count"] = state.get("retry_count", 0) + 1
        trace.append(
            {
                "node": "executor",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "success": False,
                    "error": message,
                    "retry_count": state["retry_count"],
                },
            }
        )

    return state

