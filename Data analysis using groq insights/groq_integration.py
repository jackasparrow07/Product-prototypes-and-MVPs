import os
import requests
from groq import Groq

def validate_api_key(api_key):
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def fetch_groq_models(api_key):
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [model['id'] for model in response.json()['data']]
    else:
        return []

def get_groq_insights(api_key, model, context):
    client = Groq(api_key=api_key)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant specialized in data analysis and insights. Provide concise and relevant insights based on the given context."
            },
            {
                "role": "user",
                "content": f"Analyze the following data and provide insights:\n\n{context}"
            }
        ],
        model=model,
    )
    
    return chat_completion.choices[0].message.content