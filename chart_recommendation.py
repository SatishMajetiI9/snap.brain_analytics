import json
from openai_api import call_openapi

def decide_chart_execution(user_input, query, query_result):
    chart_system_prompt = """
        You are an AI assistant that specializes in data visualization using Chartjs. 
        Your task is to analyze the output of a SQL query and recommend the best chart or graph type for visualizing the data. 
        Consider the type of data (e.g., categorical, numerical) and the user’s original question.
        Provide the output in the format that will be asked.
    """

    chart_prompt = f"""
    You are given three pieces of information:
    1. User input: The original question asked by the user in natural language i.e., {user_input}.
    2. SQL query: The SQL query that was generated to answer the user’s question i.e., {query}.
    3. SQL output: The result of the SQL query i.e., {query_result}.

    Based on these three inputs, recommend one chart type (e.g., 'bar', 'line', 'pie', 'bubble', 'doughnut', 'scatter', 'polarArea', 'radar', 'scatter') suitable for Chart.js visualization.

    Generate a JSON response with the following structure:

    - `chart_type`: The type of chart to use (e.g., 'bar', 'line', 'pie', 'bubble', 'doughnut', 'scatter', 'polarArea', 'radar', 'scatter').
    - `labels`: An array of labels for the chart's x-axis or categories.
    - `datasets`: An array of dataset objects, each containing:
        - `label`: The name of the dataset.
        - `data`: An array of data points corresponding to the labels.
        - `backgroundColor` (optional): An array of background colors for the dataset.
        - `borderColor` (optional): An array of border colors for the dataset.
        - Other Chart.js dataset options as needed.
    - `options` (optional): An object containing additional Chart.js options like titles, scales, plugins, etc.
    - `summary`: An explanation or summary on {query_result} based on the {user_input}, the {query}.

    Please ensure that:
    - All JSON keys and string values are enclosed in double quotes.
    - Any double quotes within the `code` field are escaped with backslashes.
    - The JSON structure is valid and properly formatted.
    """

    retries = 3
    last_error = None

    for attempt in range(retries):
        try:
            chart_response = call_openapi(chart_system_prompt, chart_prompt, "gpt-4o-mini")
            response = chart_response.choices[0].message.content

            cleaned_data_str = response.replace('```json\n', '').replace('```', '')
            data_json = json.loads(cleaned_data_str)
            
            return data_json
        
        except (Exception) as e:
            print(f"Attempt {attempt + 1} failed. Error: {str(e)}")
            last_error = str(e)

    return {"error": f"Failed to generate a valid chart after {retries} attempts.", "last_error": last_error}
