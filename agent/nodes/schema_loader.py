"""
Schema loader node for the LangGraph text-to-SQL agent.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from agent.state import AgentState

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "northwind.db"


def load_schema(state: AgentState) -> AgentState:
    """Load the SQLite database schema and store it in agent state."""
    trace = state.setdefault("trace", [])

    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )
            tables = [row[0] for row in cursor.fetchall()]

            schema_sections = []
            for table_name in tables:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_descriptions = ", ".join(
                    f"{column[1]} ({column[2] or 'TEXT'})" for column in columns
                )
                schema_sections.append(
                    f"Table: {table_name}\nColumns: {column_descriptions}"
                )

        state["schema"] = "\n\n".join(schema_sections)
        trace.append(
            {
                "node": "schema_loader",
                "timestamp": datetime.utcnow().isoformat(),
                "details": f"Loaded schema for {len(tables)} tables from {DB_PATH.name}.",
            }
        )
    except Exception as exc:
        state["schema"] = ""
        state["error_message"] = f"Schema loading failed: {exc}"
        trace.append(
            {
                "node": "schema_loader",
                "timestamp": datetime.utcnow().isoformat(),
                "details": f"Failed to load schema: {exc}",
            }
        )

    return state

