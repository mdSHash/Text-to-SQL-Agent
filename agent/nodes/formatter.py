"""
Answer formatter node for the LangGraph text-to-SQL agent.
"""

from __future__ import annotations

import os
from datetime import datetime

from google import genai

from agent.state import AgentState


def _format_results_for_prompt(state: AgentState) -> str:
    """Format execution results into a readable text block for the LLM prompt."""
    execution_result = state.get("execution_result", {})
    columns = execution_result.get("columns", [])
    rows = execution_result.get("data", [])

    if not rows:
        return "No rows were returned by the query."

    lines = []
    if columns:
        lines.append("Columns: " + ", ".join(str(column) for column in columns))

    for index, row in enumerate(rows, start=1):
        lines.append(f"Row {index}: {row}")

    return "\n".join(lines)


def format_answer(state: AgentState) -> AgentState:
    """Generate a natural language answer from the successful SQL execution result."""
    trace = state.setdefault("trace", [])

    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set.")

        client = genai.Client(api_key=api_key)

        prompt = (
            "You are a helpful data analyst.\n"
            "Provide a clear, concise answer to the question based on these results.\n\n"
            f"Original question:\n{state.get('question', '')}\n\n"
            f"Successful SQL query:\n{state.get('sql_query', '')}\n\n"
            f"Query results:\n{_format_results_for_prompt(state)}\n"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        final_answer = response.text.strip()

        state["final_answer"] = final_answer
        trace.append(
            {
                "node": "formatter",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "answer_preview": final_answer[:200],
                    "result_row_count": len(
                        state.get("execution_result", {}).get("data", [])
                    ),
                },
            }
        )
    except Exception as exc:
        state["final_answer"] = (
            "The SQL query executed successfully, but formatting the final answer failed. "
            f"Error: {exc}"
        )
        trace.append(
            {
                "node": "formatter",
                "timestamp": datetime.utcnow().isoformat(),
                "details": f"Failed to format final answer: {exc}",
            }
        )

    return state

