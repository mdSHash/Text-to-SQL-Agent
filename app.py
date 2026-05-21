"""
Main Streamlit application for the NL2SQL Agent.

This application provides a user-friendly interface for converting natural language
questions into SQL queries using an AI agent with full trace visualization.
Modern dark glassmorphism design with indigo/violet/cyan accents.
"""

import streamlit as st
import os
import datetime
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

from ui.components import (
    render_trace_panel,
    render_sample_questions,
    render_query_history,
    render_results,
    apply_custom_css,
    render_database_info,
    render_instructions
)
from agent.graph import run_agent


# Page Configuration
st.set_page_config(
    page_title="NL2SQL Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def check_api_key() -> bool:
    """
    Check if the Google API key is configured.

    Returns:
        True if API key is present, False otherwise.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("""
        ⚠️ **Google API Key Not Found**

        Please set your `GOOGLE_API_KEY` in the `.env` file.

        1. Copy `.env.example` to `.env`
        2. Add your Google API key
        3. Restart the application

        Get your API key from: https://makersuite.google.com/app/apikey
        """)
        st.stop()
        return False
    return True


def initialize_session_state() -> None:
    """
    Initialize Streamlit session state variables with defaults if not present.
    """
    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    if "current_result" not in st.session_state:
        st.session_state.current_result = None

    if "show_trace" not in st.session_state:
        st.session_state.show_trace = True

    if "current_trace" not in st.session_state:
        st.session_state.current_trace = []

    if "current_question" not in st.session_state:
        st.session_state.current_question = ""


def add_to_history(question: str) -> None:
    """
    Add a query to the history, keeping only the last 10 entries.

    Args:
        question: The user's question
    """
    history_entry = {
        "question": question,
        "timestamp": datetime.datetime.now().isoformat()
    }

    st.session_state.query_history.append(history_entry)

    # Keep only last 10 queries
    if len(st.session_state.query_history) > 10:
        st.session_state.query_history = st.session_state.query_history[-10:]


def execute_query(question: str) -> None:
    """
    Execute a natural language query using the agent.

    Args:
        question: The user's natural language question
    """
    if not question or not question.strip():
        st.warning("Please enter a question.")
        return

    # Show loading animation with modern dark theme
    loading_placeholder = st.empty()

    with loading_placeholder:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 50%, rgba(6, 182, 212, 0.08) 100%);
                border: 1px solid rgba(99, 102, 241, 0.2);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                padding: 2.5rem;
                border-radius: 16px;
                text-align: center;
                animation: pulse 2s infinite;
                box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
            ">
                <div style="font-size: 3.5rem; margin-bottom: 1rem; animation: pulse 1.5s infinite;">🤖</div>
                <h3 style="
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin: 0;
                    font-size: 1.4rem;
                    font-weight: 700;
                ">Agent is Processing Your Query...</h3>
                <p style="color: #94a3b8; margin: 0.75rem 0 0 0; font-size: 0.95rem;">
                    Analyzing schema → Generating SQL → Validating → Executing
                </p>
            </div>
        """, unsafe_allow_html=True)

    try:
        # Run the agent
        result = run_agent(question)

        # Clear loading message
        loading_placeholder.empty()

        # Store results in session state
        st.session_state.current_result = result
        st.session_state.current_trace = result.get("trace", [])
        st.session_state.current_question = question

        # Add to history
        add_to_history(question)

    except Exception as e:
        loading_placeholder.empty()
        st.error(f"❌ An error occurred: {str(e)}")
        st.session_state.current_result = {
            "success": False,
            "error": str(e),
            "trace": []
        }


def render_main_content() -> None:
    """
    Render the main content area with query input and results.
    """
    # Sample Questions Section
    selected_sample = render_sample_questions()

    if selected_sample:
        st.session_state.current_question = selected_sample
        st.rerun()

    # Query Input
    st.markdown("### 💬 Ask Your Question")

    user_question = st.text_area(
        "Enter your question in natural language:",
        value=st.session_state.current_question,
        height=100,
        placeholder="e.g., Which customers placed the most orders last year?",
        help="Ask any question about the Northwind database in plain English"
    )

    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        submit_button = st.button(
            "🚀 Submit Query",
            type="primary",
            use_container_width=True
        )

    with col2:
        clear_button = st.button(
            "🗑️ Clear",
            use_container_width=True
        )

    if clear_button:
        st.session_state.current_result = None
        st.session_state.current_trace = []
        st.session_state.current_question = ""
        st.rerun()

    if submit_button and user_question:
        execute_query(user_question)
        st.rerun()

    # Display Results
    if st.session_state.current_result:
        st.markdown("---")
        result = st.session_state.current_result

        # Check if execution was successful
        exec_result = result.get("execution_result", {})

        if exec_result.get("success"):
            # Display final answer
            if result.get("final_answer"):
                st.success(f"✅ **Answer:** {result['final_answer']}")

            # Display execution stats
            col1, col2, col3 = st.columns(3)

            with col1:
                retry_count = result.get("retry_count", 0)
                st.metric("Retry Count", retry_count)

            with col2:
                if "execution_time" in exec_result:
                    exec_time = exec_result["execution_time"]
                    st.metric("Execution Time", f"{exec_time:.3f}s")

            with col3:
                if "data" in exec_result:
                    row_count = len(exec_result["data"])
                    st.metric("Rows Returned", row_count)

            # Display SQL and Results
            if "sql_query" in result:
                st.markdown("---")
                render_results(exec_result, result["sql_query"])

            # Debug information
            with st.expander("🔍 Debug: View Raw Result", expanded=False):
                st.json(result)

        else:
            error_msg = result.get("error", "Unknown error occurred")
            st.error(f"❌ **Error:** {error_msg}")

            # Show any partial results if available
            if "sql_query" in result and result["sql_query"]:
                sql_display = result["sql_query"].strip()
                # Defensive strip: remove leftover language identifier artifacts
                # (e.g., "ite" from "sqlite" being partially stripped)
                if sql_display.lower().startswith("ite\n") or sql_display.lower().startswith("ite "):
                    sql_display = sql_display[3:].lstrip()
                elif sql_display.lower().startswith("ite\r\n"):
                    sql_display = sql_display[5:].lstrip()
                elif sql_display.lower().startswith("ite") and len(sql_display) > 3 and sql_display[3:].lstrip().upper().startswith("SELECT"):
                    sql_display = sql_display[3:].lstrip()
                st.markdown("### 📝 Generated SQL (Failed)")
                st.code(sql_display, language="sql")


def render_trace_sidebar() -> None:
    """
    Render the trace panel in the right column.
    """
    st.markdown("## 🔍 Agent Execution Trace")

    # Toggle for trace visibility
    show_trace = st.checkbox(
        "Show detailed trace",
        value=st.session_state.show_trace,
        help="Toggle to show/hide the agent's reasoning process"
    )
    st.session_state.show_trace = show_trace

    if show_trace:
        if st.session_state.current_trace:
            render_trace_panel(st.session_state.current_trace)
        else:
            st.info("Submit a query to see the agent's execution trace here.")


def render_sidebar() -> None:
    """
    Render the sidebar with app info, history, and database info.
    """
    with st.sidebar:
        st.markdown("# 🤖 NL2SQL Agent")
        st.markdown("Convert natural language to SQL queries")

        st.markdown("---")

        # Instructions
        render_instructions()

        st.markdown("---")

        # Query History
        selected_history = render_query_history(st.session_state.query_history)
        if selected_history:
            st.session_state.current_question = selected_history
            st.rerun()

        st.markdown("---")

        # Database Info
        render_database_info()

        st.markdown("---")

        # Footer
        st.markdown("""
        ### 🔗 Links
        - [GitHub Repository](#)
        - [Documentation](#)
        - [Report an Issue](#)

        ---

        Made with ❤️ using Streamlit & LangGraph
        """)


def main():
    """
    Main application entry point.
    Orchestrates the full layout with modern dark theme.
    """
    # Apply custom CSS from components
    apply_custom_css()

    # Check for API key (stops execution if missing)
    check_api_key()

    # Initialize session state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Modern gradient header with dark theme
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 50%, rgba(6, 182, 212, 0.08) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 2rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            animation: fadeIn 0.6s ease;
        ">
            <h1 style="
                margin: 0 0 0.5rem 0;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.5rem;
                font-weight: 800;
                letter-spacing: -0.03em;
            ">🤖 Natural Language to SQL Agent</h1>
            <p style="
                margin: 0;
                color: #94a3b8;
                font-size: 1.1rem;
                line-height: 1.6;
            ">
                Ask questions about the <strong style="color: #e2e8f0;">Northwind database</strong> in plain English and get instant SQL queries and results.
                The agent uses AI to understand your question, generate SQL, validate it, and execute it safely.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Create two-column layout: Left (60%) / Right (40%)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        render_main_content()

    with col_right:
        render_trace_sidebar()


if __name__ == "__main__":
    main()
