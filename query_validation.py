import json
from openai_api import call_openapi

def validate_sql_query(user_input, schema_data, query_result, db_type):

    query = query_result['query']
    explanation = query_result['content']

    validation_system_prompt = f"""
        You are an AI assistant with expertise in SQL query validation in {db_type}.
        Your task is to validate whether the provided SQL query is correct based on the user's question and the database schema. 
        Ensure that the query correctly answers the user's question and adheres to SQL best practices such as appropriate JOINs, filtering, aggregations, and correct column references.
    """

    validation_prompt = f"""
    The following is the schema of a {db_type} database:

    {schema_data}

    The user has asked the following question:
    "{user_input}"

    The SQL query generated to answer this question is:
    {query}

    Explanation or Plan for the Query:
    {explanation}

    Based on the provided schema and the user’s question, your task is to validate whether the SQL query is correct for the {db_type} database and whether it adheres to the syntax and best practices specific to {db_type}. 

    Focus on the following when validating the query:
    1. Does the SQL query reference the correct tables and columns from the schema to answer the user's question?
    2. Are the JOINs between tables correctly implemented based on the relationships (e.g., foreign keys) in the schema?
    3. If the query involves aggregations (e.g., SUM, COUNT, AVG), are they used correctly to answer the user’s question, following {db_type} syntax?
    4. If filtering conditions (e.g., WHERE clauses) are present, do they properly reflect the user's question and the data in the schema?
    5. If there are date-related or time-series questions, are the date functions (e.g., DATE_FORMAT, YEAR, MONTH) used correctly for {db_type}, and is the query sorted properly (e.g., by date)?
    6. If the question involves sorting (e.g., top customers, least products), is the ORDER BY clause used appropriately?
    7. Does the query handle edge cases, such as NULL values, if applicable to the user’s question or schema, according to {db_type} best practices?
    8. Does the query use the appropriate SQL functions for calculating percentages or distinct values in {db_type}, if needed?
    9. Does the query adhere to {db_type} best practices, such as indexing columns used in WHERE and JOIN clauses to optimize performance?

    Based on this validation, return one of the following JSON responses:
    - If the query is correct and answers the user’s question based on the schema and {db_type} syntax, return {{ "response": 1 }}.
    - If the query is incorrect or does not fully answer the user’s question, return {{ "response": 0 }}.

    Ensure that the response is in valid JSON format and do not include any extra commentary.
    """


    retries = 3
    for attempt in range(retries):
        try:
            validation_response = call_openapi(validation_system_prompt, validation_prompt, "gpt-4o-mini")
            response = validation_response.choices[0].message.content

            cleaned_data_str = response.replace('```json\n', '').replace('```', '')
            data_json = json.loads(cleaned_data_str) 

            return data_json

        except (Exception) as e:
            print(f"Validation attempt {attempt + 1} failed. Error: {str(e)}")
            
            if attempt == retries - 1:
                return {"error": f"Failed to validate the query after {retries} attempts.", "last_error": str(e)}
