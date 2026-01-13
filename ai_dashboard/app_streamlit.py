"""
Streamlit-based web application for Copilot Analytics.
Custom chat interface for natural language data queries.

Prerequisites:
1. Run 'dbt build' to create the database
2. Start copilot-api: npx copilot-api@latest start --rate-limit 10
3. Run: streamlit run app_streamlit.py

Access the app at: http://localhost:8501
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from copilot_vanna import CopilotAnalytics
from train_vanna import TRAINING_EXAMPLES
from config import DATABASE_PATH

# Page configuration
st.set_page_config(
    page_title="Copilot Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_analytics():
    """Initialize and cache the analytics instance with training examples."""
    analytics = CopilotAnalytics()
    analytics.connect()

    # Add training examples for better few-shot learning
    for question, sql in TRAINING_EXAMPLES:
        analytics.add_training_example(question, sql)

    return analytics


def generate_chart(df: pd.DataFrame, question: str) -> go.Figure:
    """
    Generate an appropriate chart based on the data and question.
    Uses simple heuristics to create meaningful visualizations.
    """
    if df is None or df.empty or len(df.columns) < 1:
        return None

    # Get column types
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    string_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    date_cols = [
        c for c in df.columns
        if "date" in c.lower() or "month" in c.lower() or "year" in c.lower()
    ]

    question_lower = question.lower()

    # Single value result - show as metric
    if len(df) == 1 and len(numeric_cols) == 1:
        return None  # Will show as metric in the app

    # Time series - line chart
    if date_cols and numeric_cols:
        date_col = date_cols[0]
        value_col = numeric_cols[0]

        if "trend" in question_lower or "over time" in question_lower or "monthly" in question_lower:
            fig = px.line(
                df, x=date_col, y=value_col,
                title=f"{value_col} Over Time",
                markers=True
            )
            fig.update_layout(xaxis_title="", yaxis_title=value_col)
            return fig

        # Bar chart for date data
        fig = px.bar(df, x=date_col, y=value_col, title=f"{value_col} by {date_col}")
        fig.update_layout(xaxis_title="", yaxis_title=value_col)
        return fig

    # Category breakdown - pie or bar chart
    if string_cols and numeric_cols:
        cat_col = string_cols[0]
        value_col = numeric_cols[0]

        # Pie chart for "breakdown" or percentage questions
        if "breakdown" in question_lower or "distribution" in question_lower or "percent" in question_lower:
            fig = px.pie(df, names=cat_col, values=value_col, title=f"{value_col} by {cat_col}")
            return fig

        # Horizontal bar for rankings/top queries
        if "top" in question_lower or len(df) <= 10:
            fig = px.bar(
                df, y=cat_col, x=value_col,
                title=f"{value_col} by {cat_col}",
                orientation='h'
            )
            fig.update_layout(yaxis_title="", xaxis_title=value_col)
            return fig

        # Vertical bar chart for comparisons
        fig = px.bar(
            df, x=cat_col, y=value_col,
            title=f"{value_col} by {cat_col}",
            color=cat_col
        )
        fig.update_layout(xaxis_title="", yaxis_title=value_col, showlegend=False)
        return fig

    # Two numeric columns - scatter plot
    if len(numeric_cols) >= 2:
        fig = px.scatter(
            df, x=numeric_cols[0], y=numeric_cols[1],
            title=f"{numeric_cols[1]} vs {numeric_cols[0]}"
        )
        return fig

    return None


def main():
    """Main Streamlit application."""
    # Header
    st.title("📊 Copilot Analytics")
    st.markdown("*Ask questions about your data in plain English*")

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This dashboard uses **GitHub Copilot** to convert
        your questions into SQL queries.

        **How it works:**
        1. Type a question about your data
        2. AI generates the SQL query
        3. Query runs against DuckDB
        4. Results displayed with charts
        """)

        st.divider()

        # Quick actions
        st.header("Example Questions")
        quick_queries = [
            "Show monthly revenue trends",
            "Top 10 customers by lifetime value",
            "Revenue by payment method",
            "Customers by segment",
            "Average order value",
        ]

        for query in quick_queries:
            if st.button(query, key=f"quick_{query}", use_container_width=True):
                st.session_state.pending_question = query

        st.divider()

        # Database info
        st.header("Database")
        st.code(DATABASE_PATH.name)

        if st.button("Show Schema", use_container_width=True):
            st.session_state.show_schema = True

    # Check database exists
    if not DATABASE_PATH.exists():
        st.error(f"""
        **Database not found**

        Please run the following commands first:
        ```bash
        cd dbt_project
        dbt build
        ```
        """)
        return

    # Initialize analytics
    try:
        analytics = get_analytics()
    except Exception as e:
        st.error(f"""
        **Failed to initialize analytics**

        Error: {e}
        """)
        return

    # Show schema if requested
    if st.session_state.get("show_schema"):
        with st.expander("Database Schema", expanded=True):
            st.code(analytics.get_schema())
        st.session_state.show_schema = False

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "sql" in msg and msg["sql"]:
                with st.expander("View SQL", expanded=False):
                    st.code(msg["sql"], language="sql")
            if "data" in msg and msg["data"] is not None and not msg["data"].empty:
                # Show metric for single values
                if len(msg["data"]) == 1 and len(msg["data"].columns) == 1:
                    col_name = msg["data"].columns[0]
                    value = msg["data"].iloc[0, 0]
                    st.metric(col_name, f"{value:,.2f}" if isinstance(value, float) else value)
                else:
                    st.dataframe(msg["data"], use_container_width=True)
            if "chart" in msg and msg["chart"] is not None:
                st.plotly_chart(msg["chart"], use_container_width=True)

    # Handle pending question from sidebar
    user_input = None
    if st.session_state.get("pending_question"):
        user_input = st.session_state.pending_question
        st.session_state.pending_question = None

    # Chat input
    chat_input = st.chat_input("Ask a question about your data...")
    if chat_input:
        user_input = chat_input

    # Process user input
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Generating SQL..."):
                try:
                    # Generate SQL
                    sql = analytics.generate_sql(user_input)

                    if sql:
                        st.write("Here's what I found:")

                        with st.expander("View SQL", expanded=False):
                            st.code(sql, language="sql")

                        # Execute query
                        try:
                            df = analytics.run_sql(sql)

                            if df is not None and not df.empty:
                                # Show metric for single values
                                if len(df) == 1 and len(df.columns) == 1:
                                    col_name = df.columns[0]
                                    value = df.iloc[0, 0]
                                    st.metric(col_name, f"{value:,.2f}" if isinstance(value, float) else value)
                                else:
                                    st.dataframe(df, use_container_width=True)

                                # Generate chart
                                chart = generate_chart(df, user_input)
                                if chart:
                                    st.plotly_chart(chart, use_container_width=True)

                                # Save to history
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": "Here's what I found:",
                                    "sql": sql,
                                    "data": df,
                                    "chart": chart,
                                })
                            else:
                                st.info("Query returned no results.")
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": "Query returned no results.",
                                    "sql": sql,
                                    "data": None,
                                    "chart": None,
                                })

                        except Exception as e:
                            st.error(f"Error executing query: {e}")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"Error executing query: {e}",
                                "sql": sql,
                                "data": None,
                                "chart": None,
                            })
                    else:
                        st.warning("I couldn't generate a query. Try rephrasing your question.")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "I couldn't generate a query for that question.",
                            "sql": None,
                            "data": None,
                            "chart": None,
                        })

                except Exception as e:
                    error_msg = str(e)
                    if "Connection refused" in error_msg or "connect" in error_msg.lower():
                        st.error("""
                        **Cannot connect to Copilot API**

                        Make sure copilot-api is running:
                        ```bash
                        npx copilot-api@latest start --rate-limit 10
                        ```
                        """)
                    else:
                        st.error(f"Error: {e}")

        # Rerun to update chat display
        st.rerun()


if __name__ == "__main__":
    main()
