import streamlit as st
from database_extraction import get_schema_data
from sql_execution import execute_sql
from sql_generation import sql_query_generation
from chart_recommendation import decide_chart_execution
from chart_execution import generate_chartjs_html
import pandas as pd
import os

# Set page configuration to use wide layout
st.set_page_config(layout="wide")

# Inject custom CSS to make the sidebar scrollable
st.markdown("""
    <style>
    /* Adjust the height and make the sidebar scrollable */
    section[data-testid="stSidebar"] > div:first-child {
        height: 80vh;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    # Removed the sidebar title as per your request
    st.title("Demo Insights")

    # First Expander: About
    with st.expander("**About**", expanded=True):
        st.write("""
        This is an example of an AI-driven analytics solution that answers advanced user queries on business data.
        """, unsafe_allow_html=True)

    # Second Expander: About Database
    with st.expander("**About Database**", expanded=False):
        st.write("""
        The data set can be sourced from database, CSV files, or reports. The agentic workflow determines the best way to answer the questions posed in plain English.

        The data set is a transaction database for a music store with information about:
        1. Employees
        2. Music albums
        3. Tracks
        4. Sales Invoices

        snap.brain analytics is fed with this information, and is able to reason through the data and provide advanced analytics to the user.

        snap.brain allows user-driven projects that enable custom analytics like this use-case.
        """, unsafe_allow_html=True)

    # Third Expander: Agent-driven Architecture
    with st.expander("**Agent-driven Architecture**", expanded=False):
        st.write("""
        This demo is run by the following agents:

        **Planning agent**: Creates an overall plan to decide exact steps to be followed to provide insights.

        **SQL Agent**: Processes SQL database structure and makes sense of the structure. This agent outputs SQL queries to perform the actual task.

        **SQL Validation agent**: Verifies the output of the SQL agent to fix hallucinations.

        **Visualization agent**: Decides the best way to visualize the data. Converts the data provided by the SQL agent into JSON structures for visualization using advanced charting libraries.
        """, unsafe_allow_html=True)

# Main content
st.title("snap.brain Analytics")

# Set base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# User input
user_input = st.text_input("Enter your question", "What are the top customers by total purchases?")
schema_folder = os.path.join(base_dir, 'schema')
db_type = "sqlite"

if db_type == 'sqlite':
    db_path = os.path.join(base_dir, 'db_files', 'chinook.db')
else:
    db_host = st.text_input(f"Enter your {db_type} host", "localhost")
    db_port = st.text_input(f"Enter your {db_type} port", "5432" if db_type == 'postgresql' else "3306")
    db_user = st.text_input(f"Enter your {db_type} username", "your_db_username")
    db_password = st.text_input(f"Enter your {db_type} password", "your_db_password", type='password')
    db_name = st.text_input(f"Enter your {db_type} database name", "your_db_name")

if st.button("Generate and Visualize"):
    with st.spinner("Extracting schema data..."):
        if db_type == 'sqlite':
            schema_data = get_schema_data(db_path, db_type, schema_folder)
        else:
            schema_data = get_schema_data(
                db_path=None,
                db_type=db_type,
                schema_folder=schema_folder,
                db_user=db_user,
                db_password=db_password,
                db_host=db_host,
                db_port=db_port,
                db_name=db_name
            )

    if schema_data:
        with st.spinner("Executing SQL..."):
            query_generation = sql_query_generation(user_input, schema_data, db_type)
            if 'caution' not in query_generation:
                query = query_generation['query']
                columns = query_generation['column_names']

                if db_type == 'sqlite':
                    query_result = execute_sql(db_type, db_path, query)
                else:
                    query_result = execute_sql(
                        db_type,
                        db_path=None,
                        sql_query=query,
                        db_user=db_user,
                        db_password=db_password,
                        db_host=db_host,
                        db_port=db_port,
                        db_name=db_name
                    )

                st.write("**Result**:")
                df = pd.DataFrame(query_result, columns=columns)
                df = df.reset_index(drop=True)
                df.index = df.index + 1
                st.dataframe(df)

        if 'caution' not in query_generation:
            with st.spinner("Generating chart..."):
                chart_json = decide_chart_execution(user_input, query, query_result)

                st.write("**Summary**:")
                st.write(chart_json['summary'])

                chart_html = generate_chartjs_html(chart_json)
                st.components.v1.html(chart_html, height=800)

        if 'caution' in query_generation:
            st.warning(query_generation['caution'])
    else:
        st.error("Error in extracting schema or generating query. Please check the inputs.")