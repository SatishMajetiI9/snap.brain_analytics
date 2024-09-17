import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def call_openapi(system_prompt, prompt, model):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment variables.")
    
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response
