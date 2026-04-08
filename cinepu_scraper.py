import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://cinepu.com/cast/"

def scrape_cinepu_cast():
    print(f"Fetching {URL} ...")
    response = requests.get(URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', class_='table list')
    if not table:
        print("Error: Could not find the article table.")
        return
    
    rows = table.find_all('tr')
    print(f"Found {len(rows)} entries on the first page.")
    
    results = []
    
    for row in rows:
        desc_td = row.find('td', class_='desc')
        if not desc_td:
            continue
            
        a_tag = desc_td.find('a')
        if not a_tag:
            continue
            
        link = "https://cinepu.com" + a_tag['href']
        
        # Extract title
        title_div = a_tag.find('div', class_='title')
        title = title_div.text.strip() if title_div else "No title"
        
        # Extact tags/categories
        smalls = a_tag.find_all('small')
        tags = smalls[0].text.strip() if len(smalls) > 0 else ""
        date = smalls[1].text.strip() if len(smalls) > 1 else ""
        
        # Check labels like "報酬あり"
        labels = [l.text.strip() for l in desc_td.find_all('label')]
        
        is_paid = "報酬あり" in labels
        is_ticketback = "チケットバック制" in labels
        
        # Filter (Customize this as needed)
        # For now, let's just collect everything but mark them
        
        entry = {
            "title": title,
            "url": link,
            "tags": tags,
            "date": date.replace("投稿日：", ""),
            "is_paid": is_paid,
            "is_ticketback": is_ticketback,
            "labels": labels
        }
        results.append(entry)
        
    print(f"Extracted {len(results)} items.")
    
    # Save to JSON
    output_file = "cinepu_latest.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    scrape_cinepu_cast()
