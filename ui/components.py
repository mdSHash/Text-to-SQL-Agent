"""
Modern UI components for the NL2SQL Agent Streamlit application.
Features a dark-mode glassmorphism design with smooth animations.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Optional


def apply_custom_css() -> None:
    """Inject comprehensive custom CSS for modern dark glassmorphism theme."""
    st.markdown("""
    <style>
    /* ============================================
       MODERN DARK GLASSMORPHISM THEME
       Color Palette:
       - Primary: #6366f1 (indigo)
       - Secondary: #8b5cf6 (violet)
       - Accent: #06b6d4 (cyan)
       - Success: #10b981 (emerald)
       - Error: #ef4444 (red)
       - Warning: #f59e0b (amber)
       - Background: #0f172a (slate-900)
       - Cards: #1e293b (slate-800)
       - Surface: #334155 (slate-700)
       - Text: #f8fafc (slate-50)
       - Muted: #94a3b8 (slate-400)
    ============================================ */

    /* === ANIMATIONS === */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    @keyframes glow {
        0%, 100% { box-shadow: 0 0 8px rgba(99, 102, 241, 0.3); }
        50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.6); }
    }

    /* === BASE STYLES === */
    .stApp {
        background: #0f172a !important;
        color: #f8fafc !important;
    }

    .main .block-container {
        padding-top: 2rem;
        animation: fadeIn 0.4s ease-out;
    }

    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    p, span, label, .stMarkdown {
        color: #e2e8f0 !important;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 4px;
        transition: background 0.2s;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #6366f1;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
    }

    [data-testid="stSidebar"] .stMarkdown p {
        color: #94a3b8 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }

    /* === BUTTONS === */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #f8fafc !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25) !important;
        letter-spacing: 0.01em;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4) !important;
        background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3) !important;
    }

    /* === TEXT INPUT / TEXT AREA === */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #64748b !important;
    }

    /* === EXPANDERS === */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .streamlit-expanderHeader:hover {
        border-color: rgba(99, 102, 241, 0.4) !important;
        background: rgba(30, 41, 59, 0.95) !important;
    }

    .streamlit-expanderContent {
        background: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(51, 65, 85, 0.5) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* === METRICS === */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(99, 102, 241, 0.12) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(99, 102, 241, 0.3) !important;
        transform: translateY(-1px);
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    /* === DATAFRAME === */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(51, 65, 85, 0.5) !important;
    }

    /* === CODE BLOCKS === */
    .stCodeBlock {
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
    }

    /* === ALERTS / INFO / SUCCESS / ERROR === */
    .stAlert {
        background: rgba(30, 41, 59, 0.8) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(51, 65, 85, 0.5) !important;
        animation: slideUp 0.3s ease-out;
    }

    /* === DOWNLOAD BUTTON === */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        color: #e2e8f0 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #334155 0%, #475569 100%) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border-radius: 10px 10px 0 0 !important;
        color: #94a3b8 !important;
        border: 1px solid transparent !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.15) !important;
        color: #6366f1 !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
    }

    /* === CUSTOM COMPONENT CLASSES === */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(99, 102, 241, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideUp 0.4s ease-out;
    }

    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }

    .timeline-node {
        position: relative;
        padding-left: 3rem;
        margin-bottom: 0.5rem;
        animation: slideUp 0.3s ease-out;
    }

    .timeline-icon {
        position: absolute;
        left: 0;
        top: 0;
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        z-index: 2;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .timeline-connector {
        position: absolute;
        left: 1.2rem;
        top: 2.5rem;
        width: 2px;
        height: calc(100% + 0.5rem);
        z-index: 1;
    }

    .timeline-content {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        border: 1px solid rgba(51, 65, 85, 0.5);
        transition: all 0.2s ease;
    }

    .timeline-content:hover {
        border-color: rgba(99, 102, 241, 0.3);
    }

    .sample-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(99, 102, 241, 0.1);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .sample-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        background: rgba(30, 41, 59, 0.85);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
        transform: translateY(-1px);
    }

    .section-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
    }

    .section-header h3 {
        margin: 0;
        color: #f8fafc;
        font-size: 1.2rem;
    }

    .section-header p {
        margin: 0.4rem 0 0 0;
        color: #94a3b8;
        font-size: 0.88rem;
    }

    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .history-item {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(51, 65, 85, 0.4);
        border-radius: 10px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }

    .history-item:hover {
        border-color: rgba(99, 102, 241, 0.3);
        background: rgba(30, 41, 59, 0.8);
    }

    .db-tag {
        display: inline-block;
        background: rgba(99, 102, 241, 0.12);
        color: #a5b4fc;
        padding: 0.3rem 0.7rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 0.2rem;
        border: 1px solid rgba(99, 102, 241, 0.15);
    }

    .topic-tag {
        display: inline-block;
        background: rgba(6, 182, 212, 0.1);
        color: #67e8f9;
        padding: 0.3rem 0.7rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 0.2rem;
        border: 1px solid rgba(6, 182, 212, 0.15);
    }

    .instruction-step {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(51, 65, 85, 0.3);
    }

    .instruction-step:last-child {
        border-bottom: none;
    }

    .step-number {
        min-width: 2rem;
        height: 2rem;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        color: #fff;
    }

    .results-header {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.08) 100%);
        border: 1px solid rgba(16, 185, 129, 0.15);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_trace_panel(trace: list) -> None:
    """
    Display the agent execution trace with modern timeline visualization.

    Args:
        trace: List of trace entries with keys: node, timestamp, details
    """
    if not trace:
        st.info("No trace data available yet. Submit a query to see the agent's reasoning process.")
        return

    # Node configuration mapping
    node_config = {
        "schema_loader": {"icon": "📚", "color": "#1976d2", "label": "Schema Loader"},
        "sql_generator": {"icon": "🤖", "color": "#2e7d32", "label": "SQL Generator"},
        "validator": {"icon": "✅", "color": "#388e3c", "label": "Validator"},
        "executor": {"icon": "▶️", "color": "#0288d1", "label": "Executor"},
        "error_handler": {"icon": "⚠️", "color": "#d32f2f", "label": "Error Handler"},
        "formatter": {"icon": "📝", "color": "#7b1fa2", "label": "Formatter"},
    }

    # Timeline header
    st.markdown("""
        <div class="section-header">
            <h3>🔍 Execution Timeline</h3>
            <p>Follow the agent's step-by-step reasoning process</p>
        </div>
    """, unsafe_allow_html=True)

    for idx, entry in enumerate(trace, 1):
        node_name = entry.get("node", "unknown")
        timestamp = entry.get("timestamp", "")
        details = entry.get("details", {})

        # Get node configuration
        config = node_config.get(
            node_name,
            {"icon": "🔹", "color": "#757575", "label": node_name.replace('_', ' ').title()}
        )

        # Format timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%H:%M:%S.%f")[:-3]
            except (ValueError, TypeError):
                formatted_time = timestamp
        else:
            formatted_time = "N/A"

        # Determine if this is an error entry
        is_error = node_name == "error_handler" or "error" in str(details).lower()
        timeline_color = "#d32f2f" if is_error else config["color"]

        # Render timeline node
        connector_html = ""
        if idx < len(trace):
            connector_html = f"""
                <div class="timeline-connector" style="
                    background: linear-gradient(180deg, {timeline_color} 0%, transparent 100%);
                "></div>
            """

        st.markdown(f"""
            <div class="timeline-node">
                <div class="timeline-icon" style="
                    background: linear-gradient(135deg, {timeline_color}, {timeline_color}cc);
                ">{config['icon']}</div>
                {connector_html}
                <div class="timeline-content">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: {timeline_color}; font-size: 0.95rem;">{config['label']}</strong>
                        <span class="stat-badge" style="
                            background: {timeline_color}18;
                            color: {timeline_color};
                        ">{formatted_time}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Expandable details
        if is_error:
            with st.expander("View Details", expanded=True):
                st.error("⚠️ Error occurred during execution")
                st.json(details)
        else:
            with st.expander("View Details", expanded=(idx == len(trace))):
                if isinstance(details, dict):
                    # SQL generation details
                    if "sql_query" in details:
                        st.markdown("**Generated SQL Query:**")
                        st.code(details["sql_query"], language="sql")
                        other_details = {k: v for k, v in details.items() if k != "sql_query"}
                        if other_details:
                            st.markdown("**Additional Information:**")
                            st.json(other_details)

                    # Validation details (support both "valid" and "is_valid" keys)
                    elif "valid" in details or "is_valid" in details:
                        is_valid = details.get("valid", details.get("is_valid", False))
                        if is_valid:
                            st.success("✅ SQL query passed validation")
                        else:
                            st.warning("⚠️ SQL query has validation issues")
                        other_details = {k: v for k, v in details.items() if k not in ("valid", "is_valid")}
                        if other_details:
                            st.json(other_details)

                    # Execution details with metrics
                    elif "row_count" in details:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Rows Returned", details.get("row_count", 0))
                        with col2:
                            if "execution_time" in details:
                                st.metric("Execution Time", f"{details['execution_time']:.3f}s")

                    # Default JSON display
                    else:
                        st.json(details)

                elif isinstance(details, str):
                    st.markdown(details)
                else:
                    st.write(details)


def render_sample_questions() -> Optional[str]:
    """
    Display sample questions as modern interactive cards in a two-column grid.

    Returns:
        The selected question text if clicked, None otherwise.
    """
    questions = [
        {"icon": "👥", "category": "Customers", "text": "Which customers placed the most orders last year?"},
        {"icon": "📦", "category": "Products", "text": "What are the top 5 selling products by revenue?"},
        {"icon": "🚚", "category": "Shipping", "text": "Show me all orders that were shipped late"},
        {"icon": "💼", "category": "Sales", "text": "Which sales rep has the highest average order value?"},
        {"icon": "📈", "category": "Trends", "text": "What's the month-over-month revenue trend?"},
    ]

    st.markdown("""
        <div class="section-header">
            <h3>💡 Try These Sample Questions</h3>
            <p>Click any question below to get started instantly</p>
        </div>
    """, unsafe_allow_html=True)

    selected = None

    # Two-column grid layout
    col1, col2 = st.columns(2)

    for i, q in enumerate(questions):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f"""
                <div class="sample-card">
                    <span style="font-size: 1.3rem;">{q['icon']}</span>
                    <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-left: 0.5rem;">{q['category']}</span>
                    <p style="margin: 0.4rem 0 0.6rem 0; color: #e2e8f0; font-size: 0.9rem; line-height: 1.4;">{q['text']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(
                f"{q['icon']} {q['text']}",
                key=f"sample_q_{i}",
                use_container_width=True,
            ):
                selected = q["text"]

    return selected


def render_query_history(history: list) -> Optional[str]:
    """
    Display query history in the sidebar with timestamps and clickable buttons.

    Args:
        history: List of dicts with keys: question, timestamp

    Returns:
        Selected question text if clicked, None otherwise.
    """
    if not history:
        st.info("No query history yet. Ask a question to get started!")
        return None

    selected = None

    # Show most recent first
    reversed_history = list(reversed(history))

    for i, entry in enumerate(reversed_history[:10]):
        question = entry.get("question", "")
        timestamp = entry.get("timestamp", "")

        # Truncate long questions
        display_text = question if len(question) <= 50 else question[:47] + "..."

        # Format timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%H:%M")
            except (ValueError, TypeError):
                time_str = timestamp
        else:
            time_str = ""

        # Render history item
        st.markdown(f"""
            <div class="history-item">
                <span style="color: #64748b; font-size: 0.75rem;">{time_str}</span>
            </div>
        """, unsafe_allow_html=True)

        if st.button(
            f"🕐 {display_text}",
            key=f"history_{i}",
            use_container_width=True,
        ):
            selected = question

    return selected


def render_results(execution_result: dict, sql_query: str) -> None:
    """
    Display query results with SQL code, data table, statistics, and export options.

    Args:
        execution_result: Dict with keys: data, columns, execution_time (optional)
        sql_query: The SQL query string that was executed
    """
    # SQL Query display section
    st.markdown("""
        <div class="results-header">
            <h3 style="margin: 0; color: #10b981;">✨ Query Results</h3>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("**Generated SQL:**")
    st.code(sql_query, language="sql")

    # Copy SQL button
    if st.button("📋 Copy SQL", key="copy_sql"):
        st.toast("SQL copied to clipboard!", icon="✅")

    # Check for empty results - support both formats:
    # Format 1: {"data": [...], "columns": [...]}
    # Format 2: {"results": [{"col": val, ...}, ...]}
    data = execution_result.get("data", [])
    columns = execution_result.get("columns", [])
    results = execution_result.get("results", [])

    if not data and not results:
        st.info("The query executed successfully but returned no results.")
        return

    # Create DataFrame from available data format
    if data and columns:
        df = pd.DataFrame(data, columns=columns)
    elif results:
        df = pd.DataFrame(results)
    else:
        df = pd.DataFrame(data)

    # Statistics metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        exec_time = execution_result.get("execution_time", None)
        if exec_time is not None:
            st.metric("Query Time", f"{exec_time:.3f}s")
        else:
            st.metric("Query Time", "N/A")

    # Data table
    st.markdown("")
    height = min(500, (len(df) + 1) * 35 + 3)
    st.dataframe(df, use_container_width=True, hide_index=True, height=height)

    # Action buttons
    st.markdown("")
    col_csv, col_json, col_info = st.columns(3)

    # Generate timestamp for filenames
    now = datetime.now()
    file_timestamp = now.strftime("%Y%m%d_%H%M%S")

    with col_csv:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"query_results_{file_timestamp}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_json:
        json_data = df.to_json(orient="records", indent=2) or ""
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"query_results_{file_timestamp}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_info:
        if st.button("📊 Data Info", use_container_width=True):
            with st.expander("Data Details", expanded=True):
                st.markdown("**Column Types:**")
                st.write(df.dtypes)
                st.markdown("**Statistical Summary:**")
                st.write(df.describe())


def render_database_info() -> None:
    """Display information about the Northwind database schema."""
    st.markdown("""
        <div class="glass-card">
            <h4 style="margin: 0 0 0.75rem 0; color: #f8fafc;">🗄️ Northwind Database</h4>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">
                A sample database with sales data for a specialty food company.
            </p>
            <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.5rem; font-weight: 600;">Available Tables:</p>
            <div>
                <span class="db-tag">Customers</span>
                <span class="db-tag">Orders</span>
                <span class="db-tag">Order Details</span>
                <span class="db-tag">Products</span>
                <span class="db-tag">Employees</span>
                <span class="db-tag">Suppliers</span>
                <span class="db-tag">Categories</span>
                <span class="db-tag">Shippers</span>
            </div>
            <p style="color: #94a3b8; font-size: 0.8rem; margin: 1rem 0 0.5rem 0; font-weight: 600;">Query Topics:</p>
            <div>
                <span class="topic-tag">Sales trends</span>
                <span class="topic-tag">Customer behavior</span>
                <span class="topic-tag">Product performance</span>
                <span class="topic-tag">Employee metrics</span>
                <span class="topic-tag">Order fulfillment</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_instructions() -> None:
    """Display usage instructions for the application."""
    st.markdown("""
        <div class="glass-card">
            <h4 style="margin: 0 0 1rem 0; color: #f8fafc;">📖 How to Use</h4>
            <div class="instruction-step">
                <div class="step-number">1</div>
                <div>
                    <p style="margin: 0; color: #e2e8f0; font-size: 0.9rem;"><strong>Type your question</strong></p>
                    <p style="margin: 0.2rem 0 0 0; color: #94a3b8; font-size: 0.82rem;">Ask any question about the Northwind database in plain English.</p>
                </div>
            </div>
            <div class="instruction-step">
                <div class="step-number">2</div>
                <div>
                    <p style="margin: 0; color: #e2e8f0; font-size: 0.9rem;"><strong>Review the SQL</strong></p>
                    <p style="margin: 0.2rem 0 0 0; color: #94a3b8; font-size: 0.82rem;">The agent generates and validates SQL automatically.</p>
                </div>
            </div>
            <div class="instruction-step">
                <div class="step-number">3</div>
                <div>
                    <p style="margin: 0; color: #e2e8f0; font-size: 0.9rem;"><strong>Explore results</strong></p>
                    <p style="margin: 0.2rem 0 0 0; color: #94a3b8; font-size: 0.82rem;">View data tables, download exports, and analyze results.</p>
                </div>
            </div>
            <div class="instruction-step">
                <div class="step-number">4</div>
                <div>
                    <p style="margin: 0; color: #e2e8f0; font-size: 0.9rem;"><strong>Check the trace</strong></p>
                    <p style="margin: 0.2rem 0 0 0; color: #94a3b8; font-size: 0.82rem;">See the agent's reasoning in the execution timeline.</p>
                </div>
            </div>
            <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(6, 182, 212, 0.08); border-radius: 10px; border: 1px solid rgba(6, 182, 212, 0.15);">
                <p style="margin: 0 0 0.4rem 0; color: #06b6d4; font-size: 0.85rem; font-weight: 600;">💡 Tips for Better Results</p>
                <ul style="margin: 0; padding-left: 1.2rem; color: #94a3b8; font-size: 0.82rem; line-height: 1.6;">
                    <li>Be specific about what data you want</li>
                    <li>Mention table names if you know them</li>
                    <li>Specify time ranges or filters clearly</li>
                    <li>Ask for aggregations explicitly (sum, average, count)</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)
