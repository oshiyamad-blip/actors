import requests
import re
import os
import time
from location_filter import is_valid_location

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
        
    # 3. Exclude if location is specified outside of Tokyo/Suburbs
    if not is_valid_location(target):
        return True
        
    return False

def is_recruitment_ended(url_text):
    if not url_text:
        return False
    try:
        # User-Agent to avoid simple blocks
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url_text, headers=headers, timeout=10)
        if res.status_code == 404:
            return True
        html = res.text
        if "募集終了" in html or "受付終了" in html or "応募は締め切りました" in html or "募集を終了" in html:
            return True
    except Exception as e:
        print(f"Error checking {url_text}: {e}")
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
            # Find title, tags, and URL property
            title_text = ""
            tags_text = ""
            url_text = ""
            for prop_name, prop_data in page["properties"].items():
                if prop_data["type"] == "title":
                    if prop_data["title"]:
                        title_text = prop_data["title"][0]["plain_text"]
                elif prop_name == "タグ":
                    if "rich_text" in prop_data and prop_data["rich_text"]:
                        tags_text = prop_data["rich_text"][0]["plain_text"]
                elif prop_name == "URL":
                    url_text = prop_data.get("url", "")
                    
            if not title_text:
                continue
                
            is_ineligible = is_ineligible_project(title_text, tags_text)
            
            # Check for URL end status if it's not already ineligible
            is_ended = False
            if not is_male_only_project(title_text) and not is_ineligible:
                is_ended = is_recruitment_ended(url_text)
                time.sleep(0.5) # Sleep slightly to avoid hammering servers too hard
                
            if is_male_only_project(title_text) or is_ineligible or is_ended:
                reason = "ENDED" if is_ended else "INELIGIBLE/MALE-ONLY"
                print(f"DELETING ({reason}): {title_text}")
                requests.patch(f"https://api.notion.com/v1/pages/{page['id']}", headers=headers, json={"archived": True})
                deleted += 1
                
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")
            
    print(f"Checked {total} items, deleted {deleted} male-only items.")

if __name__ == "__main__":
    cleanup_notion()
