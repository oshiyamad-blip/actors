import requests
import re
import os

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "ntn_E1201788098aXe4gi8shMjzJ7BW2MwvHVMvRjr8mZh6bSs")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "33c047a1-d4c2-8059-8acf-da3c0cd61364")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def is_male_only_project(title):
    t = title.lower()
    if re.search(r'(男女|女|ヒロイン|お母さん|母親|主婦|娘|ガール|姉|妹)', t):
        return False
    
    if re.search(r'(男性|男|ボーイズ|おじさん|お爺さん|彼氏|夫|兄|弟|オジサン)', t):
        return True
        
    return False

def is_ineligible_project(title, tags):
    target = title + " " + tags
    
    # 1. Exclude if keyword matches
    if any(kw in target for kw in ["所属", "モデル"]):
        return True
        
    # 2. Exclude if it lacks target genres
    if not ("映画" in target or "ドラマ" in target):
        return True
        
    return False

def cleanup_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    has_more = True
    next_cursor = None
    deleted = 0
    total = 0
    
    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor
            
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
        
        for page in data.get("results", []):
            total += 1
            # Find title and tags property
            title_text = ""
            tags_text = ""
            for prop_name, prop_data in page["properties"].items():
                if prop_data["type"] == "title":
                    if prop_data["title"]:
                        title_text = prop_data["title"][0]["plain_text"]
                elif prop_name == "タグ":
                    if "rich_text" in prop_data and prop_data["rich_text"]:
                        tags_text = prop_data["rich_text"][0]["plain_text"]
                    
            if not title_text:
                continue
                
            if is_male_only_project(title_text) or is_ineligible_project(title_text, tags_text):
                print(f"DELETING INELIGIBLE: {title_text}")
                requests.patch(f"https://api.notion.com/v1/pages/{page['id']}", headers=headers, json={"archived": True})
                deleted += 1
                
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")
            
    print(f"Checked {total} items, deleted {deleted} male-only items.")

if __name__ == "__main__":
    cleanup_notion()
