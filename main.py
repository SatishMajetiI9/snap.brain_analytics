import streamlit as st
from database_extraction import get_schema_data
from sql_execution import execute_sql
from sql_generation import sql_query_generation
from chart_recommendation import decide_chart_execution
from chart_execution import generate_chartjs_html
import pandas as pd
import os

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .css-abcdefg.hijklmnop {
        height: 80vh;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("snap.brain Analytics Menu")

    with st.expander("About Database", expanded=True):
        st.write("""
            This is an example of an AI-driven analytics solution that answers advanced user queries on business data. 

            The data set can be sourced from database, CSV files, or reports. The agentic workflow determines the best way to answer the questions posed in plain English.

            The data set is a transaction database for a music store with information about:
            1. Employees
            2. Music albums
            3. Tracks 
            4. Sales Invoices

            snap.brain analytics is fed with this information, and is able to reason through the data and provide advanced analytics to the user. 

            snap.brain allows user-driven projects that enable custom analytics like this use-case.
        """, unsafe_allow_html=True)

    with st.expander("Agent-driven Architecture", expanded=False):
        st.write("""
            This demo is run by the following agents:

            1. **Planning agent**: Creates an overall plan to decide exact steps to be followed to provide insights. 

            2. **SQL Agent**: Processes SQL database structure and makes sense of the structure. This agent outputs SQL queries to perform the actual task. 

            3. **SQL Validation agent**: Verifies the output of the SQL agent to fix hallucinations. 

            4. **Visualization agent**: Decides the best way to visualize the data. Converts the data provided by the SQL agent into JSON structures for visualization using advanced charting libraries.
        """, unsafe_allow_html=True)

st.title("snap.brain Analytics")

base_dir = os.path.dirname(os.path.abspath(__file__))
user_input = st.text_input("Enter your question", "What are the top customers by total purchases?")
schema_folder = os.path.join(base_dir, 'schema')
db_type = "sqlite"
# schema_folder = st.text_input("Enter the path of the schema folder", "D:/Gen AI/Sql2Viz/viz/txt2viz/schema")
# db_type = st.selectbox("Select Database Type", ["sqlite", "postgresql", "mysql"])

if db_type == 'sqlite':
    # db_path = st.text_input("Enter the path of the SQLite database", "D:/Gen AI/Sql2Viz/viz/txt2viz/db_files/chinook.db")
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
            schema_data = get_schema_data(db_path=None, db_type=db_type, schema_folder=schema_folder,
                                          db_user=db_user, db_password=db_password, db_host=db_host, db_port=db_port, db_name=db_name)

    if schema_data:
        # st.write("Schema data loaded successfully!")
        # with st.spinner("Generating SQL query..."):
        with st.spinner("Executing SQL..."):
            query_generation = sql_query_generation(user_input, schema_data, db_type)
            query = query_generation['query']
            columns = query_generation['column_names']
            # st.code(query, language='sql')

        # with st.spinner("Executing SQL query..."):
            if db_type == 'sqlite':
                query_result = execute_sql(db_type, db_path, query)
            else:
                query_result = execute_sql(db_type, db_path=None, sql_query=query,
                                           db_user=db_user, db_password=db_password, db_host=db_host, db_port=db_port, db_name=db_name)
            
            st.write("**Result**: ")
            df = pd.DataFrame(query_result, columns=columns)
            df = df.reset_index(drop=True)
            df.index = df.index + 1
            st.dataframe(df)

        # with st.spinner("Deciding chart type..."):
        with st.spinner("Generating chart..."):

            chart_json = decide_chart_execution(user_input, query, query_result)
            # st.write("Chart configuration:")
            # st.json(chart_json)

            st.write("**Summary**: ")
            st.write(chart_json['summary'])

        # with st.spinner("Generating chart..."):
            chart_html = generate_chartjs_html(chart_json)
            st.components.v1.html(chart_html, height=800)

    else:
        st.error("Error in extracting schema or generating query. Please check the inputs.")