import requests
import json
import time
import re

import os

# GitHub Actions等の環境変数からトークンを取得し、なければローカル用を使用
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "ntn_E1201788098aXe4gi8shMjzJ7BW2MwvHVMvRjr8mZh6bSs")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "33c047a1-d4c2-8059-8acf-da3c0cd61364")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def setup_database_properties():
    print("Updating Database schema with Target Age and Genre...")
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    
    payload = {
        "properties": {
            "ジャンル": {"select": {
                "options": [
                    {"name": "映像", "color": "blue"},
                    {"name": "舞台", "color": "green"},
                    {"name": "未分類", "color": "default"}
                ]
            }}
        }
    }
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("Failed to update database schema:")
        print(response.text)
    else:
        print("Database schema updated successfully.")

def determine_age(title):
    title_lower = title.lower()
    if re.search(r'(20代|20歳|十代|10代|大学生|高校生|学生|若手|ヒロイン|25歳)', title_lower):
        if not re.search(r'(30代|40代|50代|シニア)', title_lower):
            return "20代前半向け"
    if re.search(r'(30代|アラフォー|35歳|母親|主婦|40代|妻|ミドル)', title_lower):
        return "30代後半向け"
    return "共通・不問"

def determine_genre(title, tags):
    target = (title + tags).lower()
    if re.search(r'(舞台|演劇|公演|ミュージカル|劇団)', target):
        return "舞台"
    if re.search(r'(映画|映像|cm|ドラマ|mv|ショート|広告|pv)', target):
        return "映像"
    return "未分類"

def is_extra_project(title, tags):
    target = (title + tags).lower()
    # If explicitly mentioning extra, return True
    if re.search(r'(エキストラ|通行人|スタンドイン|協力者|無報酬|交通費のみ|ノーギャラ)', target):
        return True
    return False

def upload_from_file(filename, default_media="シネマプランナーズ"):
    print(f"Reading data from {filename}")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception as e:
        print(f"Error reading JSON {filename}: {e}")
        return

    filtered_items = []
    for item in items:
        # Check paid
        if not item.get("is_paid"):
            continue
        # Check extra
        if is_extra_project(item["title"], item["tags"]):
            continue
        filtered_items.append(item)
            
    print(f"Found {len(filtered_items)} valid, non-extra, paid items from {filename}.")

    url = "https://api.notion.com/v1/pages"
    count = 0
    
    for item in filtered_items[:10]:
        target_age = determine_age(item["title"])
        genre = determine_genre(item["title"], item["tags"])
        
        page_payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "title": {"title": [{"text": {"content": item["title"][:200]}}]},
                "URL": {"url": item["url"]},
                "投稿日": {"rich_text": [{"text": {"content": item["date"][:100]}}]},
                "媒体": {"select": {"name": default_media}},
                "タグ": {"rich_text": [{"text": {"content": item["tags"][:100]}}]},
                "対象年代": {"select": {"name": target_age}},
                "ジャンル": {"select": {"name": genre}}
            }
        }
        res = requests.post(url, headers=headers, json=page_payload)
        if res.status_code == 200:
            count += 1
        else:
            print(f"Failed to upload {item['title'][:20]}: {res.text}")
        time.sleep(0.3) 
        
    print(f"Successfully uploaded {count} items from {filename} to Notion!")

if __name__ == "__main__":
    setup_database_properties()
    upload_from_file("cinepu_latest.json", "シネマプランナーズ")
    upload_from_file("debut_latest.json", "Audition & Debut")
    upload_from_file("twitter_latest.json", "X (Twitter)")
