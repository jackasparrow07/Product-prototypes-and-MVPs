import json
from datetime import datetime

def load_conversations(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def format_message(timestamp):
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return dt.strftime("%Y-%m-%d %H:%M:%S")