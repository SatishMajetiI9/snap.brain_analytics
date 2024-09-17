import os
import sqlite3
import pymysql
import psycopg2
from openai_api import call_openapi

# SQLite
def extract_sqlite_schema(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema = []
        for table in tables:
            table_name = table[0]
            schema.append(f"Table: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            schema.append("Columns:")
            for col in columns:
                schema.append(f"  {col[1]} ({col[2]})")
            schema.append("")
        conn.close()
        return "\n".join(schema)

    except sqlite3.Error as e:
        print(f"Error generating SQLite schema report: {str(e)}")
        return None

# MySQL
def extract_mysql_schema(db_user, db_password, db_host, db_port, db_name):
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            db=db_name,
            port=int(db_port)
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        schema = []
        for table in tables:
            table_name = table[0]
            schema.append(f"Table: {table_name}")
            cursor.execute(f"DESCRIBE {table_name};")
            columns = cursor.fetchall()
            schema.append("Columns:")
            for col in columns:
                schema.append(f"  {col[0]} ({col[1]})")
            schema.append("")
        conn.close()
        return "\n".join(schema)

    except pymysql.MySQLError as e:
        print(f"Error extracting MySQL schema: {e}")
        return None

# PostgreSQL
def extract_postgresql_schema(db_user, db_password, db_host, db_port, db_name):
    try:
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name,
            port=db_port
        )
        cursor = conn.cursor()
        cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        """)
        tables = cursor.fetchall()

        schema = []
        for table in tables:
            table_name = table[0]
            schema.append(f"Table: {table_name}")
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
            columns = cursor.fetchall()
            schema.append("Columns:")
            for col in columns:
                schema.append(f"  {col[0]} ({col[1]})")
            schema.append("")
        conn.close()
        return "\n".join(schema)

    except psycopg2.Error as e:
        print(f"Error extracting PostgreSQL schema: {e}")
        return None