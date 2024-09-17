import os
from openai_api import call_openapi
from schema_extractors import extract_sqlite_schema, extract_mysql_schema, extract_postgresql_schema

def extract_database_information(db_path, db_type, schema_folder, db_user=None, db_password=None, db_host=None, db_port=None, db_name=None):
    db_name = db_name if db_name else os.path.splitext(os.path.basename(db_path))[0]
    schema_file = os.path.join(schema_folder, f"{db_name}-{db_type}.txt")

    if db_type == 'sqlite':
        schema_report = extract_sqlite_schema(db_path)
    # elif db_type == 'mysql':
    #     schema_report = extract_mysql_schema(db_user, db_password, db_host, db_port, db_name)
    elif db_type == 'postgresql':
        schema_report = extract_postgresql_schema(db_user, db_password, db_host, db_port, db_name)
    else:
        print(f"Unsupported database type: {db_type}")
        return False

    if not schema_report:
        return False

    system_prompt = """
    You are an AI assistant with expertise in database schemas and relationships. 
    Your task is to analyze the schema information of a database, understand the relationships between tables, 
    and provide a summary of each table and its relationships, including primary keys, foreign keys, and inferred relationships.
    """

    user_prompt = f"""
    The following is the schema report of a database:

    {schema_report}

    Please provide a detailed summary of each table and its relationships, including:
    1. Primary keys for each table.
    2. Foreign key relationships between tables.
    3. Any inferred relationships if no explicit foreign keys exist.
    """

    response = call_openapi(system_prompt, user_prompt, "gpt-4o-mini")
    relationship_summary = response.choices[0].message.content

    if not os.path.exists(schema_folder):
        os.makedirs(schema_folder)

    with open(schema_file, 'w', encoding='utf-8') as file:
        file.write(schema_report + '\n' + relationship_summary)

    print(f"Relationship summary saved to {schema_file}.")
    return True

def get_schema_data(db_path, db_type, schema_folder, db_user=None, db_password=None, db_host=None, db_port=None, db_name=None):
    if db_type == "sqlite":
        db_name = os.path.splitext(os.path.basename(db_path))[0]
    schema_file = os.path.join(schema_folder, f"{db_name}-{db_type}.txt")

    if os.path.exists(schema_file):
        print(f"{db_name}-{db_type}.txt file exists!")
        with open(schema_file, 'r') as file:
            schema_data = file.read()
            return schema_data       
    else:
        print(f"{db_name}-{db_type}.txt file does not exist inside {schema_folder}!")
        if extract_database_information(db_path, db_type, schema_folder, db_user, db_password, db_host, db_port, db_name):
            print(f"{db_name}-{db_type}.txt file created!")
            with open(schema_file, 'r') as file:
                schema_data = file.read()
                return schema_data
        else:
            return False