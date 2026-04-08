import requests
import json
import sys

NOTION_TOKEN = "ntn_E1201788098aXe4gi8shMjzJ7BW2MwvHVMvRjr8mZh6bSs"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def search_notion():
    url = "https://api.notion.com/v1/search"
    payload = {
        "filter": {
            "value": "database",
            "property": "object"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
        
    data = response.json()
    if not data.get("results"):
        print("No databases found. Make sure you have connected the integration to the database page.")
        return
        
    db = data["results"][0]
    db_id = db["id"]
    title_arr = db.get("title", [])
    title = title_arr[0]["plain_text"] if title_arr else "Untitled"
    
    print(f"Found Database ID: {db_id}")
    print(f"Database Title: {title}")
    
    properties = list(db["properties"].keys())
    print(f"Properties available: {properties}")

if __name__ == "__main__":
    search_notion()
