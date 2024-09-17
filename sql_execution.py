import sqlite3
import psycopg2
# import mysql.connector

def execute_sql(db_type: str, db_path: str, sql_query: str, **kwargs) -> str:
    try:
        conn = None
        cursor = None
        
        if db_type == 'sqlite':
            conn = sqlite3.connect(db_path)
        elif db_type == 'postgresql':
            conn = psycopg2.connect(
                dbname=kwargs.get('db_name', ''),
                user=kwargs.get('db_user', ''),
                password=kwargs.get('db_password', ''),
                host=kwargs.get('db_host', 'localhost'),
                port=kwargs.get('db_port', 5432)
            )
        # elif db_type == 'mysql':
        #     conn = mysql.connector.connect(
        #         database=kwargs.get('db_name', ''),
        #         user=kwargs.get('db_user', ''),
        #         password=kwargs.get('db_password', ''),
        #         host=kwargs.get('db_host', 'localhost'),
        #         port=kwargs.get('db_port', 3306)
        #     )
        else:
            return f"Unsupported database type: {db_type}"

        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        if sql_query.strip().lower().startswith("select"):
            results = cursor.fetchall()
        else:
            conn.commit()
            results = "Query executed successfully. No results to display."
    
    except (sqlite3.Error, psycopg2.Error, mysql.connector.Error) as e:
        results = f"SQL execution failed. Error:\n{str(e)}"
    except Exception as ex:
        results = f"An error occurred: {str(ex)}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return results
