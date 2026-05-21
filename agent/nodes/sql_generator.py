"""
SQL generator node for the LangGraph text-to-SQL agent.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime

from google import genai

from agent.state import AgentState

# Configure logging
logger = logging.getLogger(__name__)


def generate_sql(state: AgentState) -> AgentState:
    """Generate a SQLite query from the user's natural language question."""
    trace = state.setdefault("trace", [])
    sql_history = state.setdefault("sql_history", [])

    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set.")

        client = genai.Client(api_key=api_key)

        retry_count = state.get("retry_count", 0)
        retry_context = ""
        if retry_count > 0:
            previous_attempts = "\n".join(
                f"Attempt {index + 1}: {query}"
                for index, query in enumerate(sql_history)
            )
            retry_context = (
                "\nPrevious SQL attempts:\n"
                f"{previous_attempts}\n"
                f"Last execution error:\n{state.get('error_message', '')}\n"
                "Generate a corrected SQL query that avoids the previous error.\n"
            )

        prompt = (
            "You are an expert SQLite query generator.\n"
            "Generate a SQLite query for the user's request using only the schema provided.\n"
            "Return ONLY the SQL query, no explanations.\n\n"
            f"Database schema:\n{state.get('schema', '')}\n\n"
            f"User question:\n{state.get('question', '')}\n"
            f"{retry_context}"
        )

        logger.info("Sending request to Gemini API...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # Extract text from response with proper error handling
        if not response:
            raise ValueError("Received empty response from Gemini API")
        
        # Get the text response
        if hasattr(response, 'text') and response.text:
            sql_text = response.text
        elif hasattr(response, 'candidates') and response.candidates:
            # Try to extract from candidates if text attribute doesn't exist
            sql_text = response.candidates[0].content.parts[0].text
        else:
            raise ValueError(f"Unable to extract text from API response: {response}")
        
        logger.info(f"Raw API response: {sql_text[:200]}...")  # Log first 200 chars
        
        # Clean up the response
        generated_sql = sql_text.strip()
        
        # Remove markdown code blocks if present
        if generated_sql.startswith('```'):
            # Split by ``` and get the content between the first pair
            parts = generated_sql.split('```')
            if len(parts) >= 3:
                # Get the code block content (index 1)
                code_block = parts[1]
                # Remove language identifier if present (e.g., 'sql', 'sqlite')
                if code_block.startswith('sqlite'):
                    code_block = code_block[6:]
                elif code_block.startswith('SQLite'):
                    code_block = code_block[6:]
                elif code_block.startswith('SQLITE'):
                    code_block = code_block[6:]
                elif code_block.startswith('sql'):
                    code_block = code_block[3:]
                elif code_block.startswith('SQL'):
                    code_block = code_block[3:]
                generated_sql = code_block.strip()
            else:
                # Fallback: just remove all backticks and language identifiers
                generated_sql = generated_sql.replace('```', '').strip()
                # Remove leading language identifier if present
                if generated_sql.startswith('sqlite'):
                    generated_sql = generated_sql[6:].strip()
                elif generated_sql.startswith('SQLite'):
                    generated_sql = generated_sql[6:].strip()
                elif generated_sql.startswith('SQLITE'):
                    generated_sql = generated_sql[6:].strip()
                elif generated_sql.startswith('sql'):
                    generated_sql = generated_sql[3:].strip()
                elif generated_sql.startswith('SQL'):
                    generated_sql = generated_sql[3:].strip()
        
        # Final validation
        if not generated_sql:
            raise ValueError("Generated SQL query is empty after cleaning")
        
        # Check if the response is an error message instead of SQL
        if generated_sql.lower().startswith('failed to') or generated_sql.lower().startswith('error'):
            raise ValueError(f"API returned an error message: {generated_sql}")
        
        logger.info(f"Generated SQL: {generated_sql}")
        
        state["sql_query"] = generated_sql
        sql_history.append(generated_sql)
        trace.append(
            {
                "node": "sql_generator",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "retry_count": retry_count,
                    "generated_sql": generated_sql,
                },
            }
        )
    except ValueError as ve:
        # Handle validation errors (empty response, error messages, etc.)
        error_msg = f"SQL generation failed: {str(ve)}"
        logger.error(error_msg)
        state["sql_query"] = ""
        state["error_message"] = error_msg
        trace.append(
            {
                "node": "sql_generator",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "error": error_msg,
                    "error_type": "validation_error"
                },
            }
        )
    except AttributeError as ae:
        # Handle API response structure issues
        error_msg = f"Failed to parse API response: {str(ae)}"
        logger.error(error_msg)
        state["sql_query"] = ""
        state["error_message"] = error_msg
        trace.append(
            {
                "node": "sql_generator",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "error": error_msg,
                    "error_type": "response_parsing_error"
                },
            }
        )
    except Exception as exc:
        # Handle all other errors (API errors, network issues, etc.)
        error_msg = f"SQL generation failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        state["sql_query"] = ""
        state["error_message"] = error_msg
        trace.append(
            {
                "node": "sql_generator",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "error": error_msg,
                    "error_type": "general_error"
                },
            }
        )

    return state

