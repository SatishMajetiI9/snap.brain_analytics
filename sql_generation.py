import json
from openai_api import call_openapi
from query_validation import validate_sql_query

def sql_query_generation(user_input, schema_data, db_type):
    query_system_prompt = f"""
                You are an AI assistant with expertise in database schemas and SQL query generation in {db_type}. 
                Your task is to generate only read-only SQL queries based on the user's question and the provided database schema and relationships.
                You are prohibited from generating queries that modify data, such as `CREATE`, `UPDATE`, `DELETE`, or any other data-modifying operations.
                If the user's input contains requests for such operations, or if the generated query would modify data, 
                return a caution message instead of generating the query.
            """
    query_prompt = f"""
            The following is the schema report of a database: 

            {schema_data}

            User Question: {user_input}

            if: 
                the input suggests modifying data, return a caution message instead of generating a query.
                Do not perform any operations that modify the data, such as `CREATE`, `UPDATE`, or `DELETE`. 

                Here is a concise list of keywords that typically indicate data-modifying operations in SQL:
                    INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, TRUNCATE, MERGE, REPLACE, RENAME, GRANT, REVOKE, LOCK,
                    SET, LOAD DATA, ADD, CASCADE, DISABLE, ENABLE, RESTART, VACUUM, REINDEX, CHECKPOINT, CLUSTER, TRIGGER,
                    PARTITION, ROLLBACK, COMMIT, SAVEPOINT, EXEC.
                These keywords are associated with commands that modify data or the structure of a database.
            
                Return the output in JSON format:
                    return a JSON response with the `caution` key and an appropriate message. 
                    Message should be in a way like "You do not have permission to CREATE, UPDATE, or DELETE any records in the database. You can only read the data that is already present. Please try again."

            else:
            
                Based on the above schema and relationships, generate a SQL query that accurately answers the user's question in {db_type}.

                Tips to remember:
                1. When ever you encounter in the {user_input} terms like `top customers`, `top countries`, `top brands` or in the opposite way like `least customers`, `least brands`, only provide 5-10 records unless the user specifies a specific count.
                2. When multiple tables are involved in the schema, ensure that you use the appropriate JOIN operations (INNER JOIN, LEFT JOIN, etc.) based on the relationships (primary key and foreign key).
                3. If the user question involves aggregations such as `total`, `average`, `count`, or `sum`, ensure that you use the relevant SQL functions such as `SUM()`, `COUNT()`, `AVG()`, or `GROUP BY` as necessary.
                4. In cases where there are date-related queries such as `sales over time` or `latest transactions`, ensure to use date functions (e.g., `DATE_FORMAT()`, `YEAR()`, `MONTH()`, `DAY()`) and remember to sort the result set by the date column in descending order to show the latest records first.
                5. If the user input contains terms like `customers from specific countries` or `products from specific categories`, use `WHERE` clauses with appropriate filters, ensuring you use SQL operators like `=`, `IN`, or `LIKE` to capture the user's intent.
                6. If the user requests a percentage calculation, include the proper SQL expressions to calculate the percentage, e.g., `COUNT(column)/SUM(column) * 100 AS percentage`.
                7. For performance reasons, always use indexed columns for `WHERE` clauses, `ORDER BY` clauses, and JOINs to make the query more efficient.
                8. When dealing with large datasets or complex queries, ensure you limit the output using `LIMIT` in the query to avoid returning an excessive number of records, especially if the user doesn't ask for a specific limit.
                9. If there are nullable columns involved in the schema, always use appropriate null handling (e.g., `IS NULL`, `IS NOT NULL`) when the user queries such columns.
                10. In cases where users ask for `distinct values` or `unique entries`, use `DISTINCT` in the SQL query to eliminate duplicate values.
                
                Return the output in JSON format.
                There should be three keys: `query` for the SQL query, `column_names` (in an array) of the table when the Query will be executed and `content` for the explanation or plan used to create the query.
        """

    retries = 3
    last_error = None

    for attempt in range(retries):
        try:
            query_response = call_openapi(query_system_prompt, query_prompt, "gpt-4o-mini")
            response = query_response.choices[0].message.content

            cleaned_data_str = response.replace('```json\n', '').replace('```', '')
            generated_query = json.loads(cleaned_data_str)

            if 'caution' not in generated_query:
                validation_response = validate_sql_query(user_input, schema_data, generated_query, db_type)
                if validation_response.get("response") == 1:
                    return generated_query
                else:
                    print(f"Validation failed for generated query. Attempt {attempt + 1}")
            if 'caution' in generated_query:
                return generated_query
                
        except (Exception) as e:
            print(f"Attempt {attempt + 1} failed. Error: {str(e)}")
            last_error = str(e)

        if attempt == retries - 1:
            return {"error": f"Failed to generate a valid query after {retries} attempts.", "last_error": last_error}
