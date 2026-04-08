import requests
from bs4 import BeautifulSoup
import json

def scrape_debut():
    url = "https://audition-debut.com/audition/"
    print(f"Fetching {url} ...")
    response = requests.get(url)
    response.encoding = response.apparent_encoding # Fix mangled charset
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # We don't know the exact class, let's find links inside some div
    items = []
    
    for a in soup.find_all('a'):
        href = a.get('href', "")
        if "audition/list" in href or "audition/detail" in href:
            text = a.text.strip().replace('\n', '')
            if len(text) > 5 and text not in [i["title"] for i in items]:
                link = href if href.startswith("http") else "https://audition-debut.com" + href
                items.append({
                    "title": text,
                    "url": link,
                    "tags": "[デビュー][オーディション]",
                    "date": "2026-04",
                    "is_paid": True, # For now
                    "is_ticketback": False
                })
    
    print(f"Found {len(items)} items")
    
    with open("debut_latest.json", "w", encoding="utf-8") as f:
        json.dump(items[:15], f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_debut()
