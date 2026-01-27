import os
import json
from openai import OpenAI

def list_assistants():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        api_key = config.get('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)
        
        print("--- Listing Assistants ---")
        assistants = client.beta.assistants.list(limit=20)
        for asst in assistants.data:
            print(f"ID: {asst.id} | Name: {asst.name}")
        print("--------------------------")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_assistants()
