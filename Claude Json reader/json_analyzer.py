import json
from collections import Counter
import sys

def analyze_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return "Error: File not found."
    except json.JSONDecodeError:
        return "Error: Invalid JSON format in the file."

    if not data:
        return "Error: The file is empty or contains no valid JSON objects."

    analysis = {
        "structure": "unknown",
        "total_items": 0,
        "keys_at_root": set(),
        "nested_structures": Counter(),
        "value_types": Counter(),
        "sample": None
    }

    def analyze_item(item, depth=0):
        if isinstance(item, dict):
            analysis["nested_structures"]["dict"] += 1
            for key, value in item.items():
                if depth == 0:
                    analysis["keys_at_root"].add(key)
                analysis["value_types"][type(value).__name__] += 1
                analyze_item(value, depth + 1)
        elif isinstance(item, list):
            analysis["nested_structures"]["list"] += 1
            for value in item:
                analysis["value_types"][type(value).__name__] += 1
                analyze_item(value, depth + 1)
        else:
            analysis["value_types"][type(item).__name__] += 1

    if isinstance(data, list):
        analysis["structure"] = "list_of_items"
        analysis["total_items"] = len(data)
        for item in data:
            analyze_item(item)
        analysis["sample"] = data[0] if data else None
    elif isinstance(data, dict):
        analysis["structure"] = "single_item"
        analysis["total_items"] = 1
        analyze_item(data)
        analysis["sample"] = data
    else:
        return "Error: Unexpected root structure in JSON file."

    return generate_markdown(analysis)

def generate_markdown(analysis):
    md = "# JSON Structure Analysis\n\n"
    
    md += f"## Overview\n"
    md += f"- Structure: {analysis['structure']}\n"
    md += f"- Total items: {analysis['total_items']}\n"
    md += f"- Keys at root level: {', '.join(sorted(analysis['keys_at_root']))}\n\n"
    
    md += f"## Nested Structures\n"
    for structure, count in analysis['nested_structures'].items():
        md += f"- {structure.capitalize()}: {count}\n"
    md += "\n"
    
    md += f"## Value Types\n"
    for type_name, count in analysis['value_types'].items():
        md += f"- {type_name}: {count}\n"
    md += "\n"
    
    md += f"## Sample Item\n"
    md += "```json\n"
    md += json.dumps(analysis['sample'], indent=2)
    md += "\n```\n"

    return md

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python json_analyzer.py <path_to_conversations.json>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analysis_result = analyze_json_file(file_path)
    print(analysis_result)