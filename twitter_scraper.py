import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime
from location_filter import is_valid_location

def scrape_twitter_via_yahoo():
    # 検索クエリ： キャスト募集 -エキストラ
    query = 'キャスト募集 -エキストラ'
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_query}"
    
    print(f"Fetching Twitter info from Yahoo Realtime: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching Yahoo Realtime: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    items = []
    
    """
    Yahooリアルタイム検索のDOMは複雑なため、
    簡易的ですがテキストブロックを抽出する処理を行います。
    ※本番環境ではAPI利用を推奨しますが、暫定的な「簡易手法」として実装しています。
    """
    # Yahoo Realtime gives us timeline items, but without full rendering we must parse JSON inside the HTML if available, or just fallback to simple div parsing
    # Here we simulate the extraction for the demo:
    tweets = soup.find_all('div', class_='Tweet_body__n_p0s')
    
    # If standard class isn't found due to Yahoo's obfuscation, we fall back to generic text
    if not tweets:
        for text_block in soup.find_all('span'):
            t = text_block.text.strip()
            if "キャスト募集" in t and len(t) > 20: # arbitrary minimum length
                valid_genre = "映画" in t or "ドラマ" in t
                is_excluded = any(kw in t for kw in ["所属", "モデル"])
                is_valid_area = is_valid_location(t)
                if valid_genre and is_valid_area and not is_excluded:
                    items.append({
                        "title": t[:100] + "...",
                        "url": "https://twitter.com/search?q=" + encoded_query,
                        "tags": "[X/Twitter]",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "is_paid": True, # assume valid for Notion upload tracking
                        "is_ticketback": False
                    })
    else:
        for tweet in tweets:
            t = tweet.text.strip()
            valid_genre = "映画" in t or "ドラマ" in t
            is_excluded = any(kw in t for kw in ["所属", "モデル"])
            is_valid_area = is_valid_location(t)
            if valid_genre and is_valid_area and not is_excluded:
                items.append({
                    "title": t[:100] + "...",
                    "url": "https://twitter.com/search?q=" + encoded_query,
                    "tags": "[X/Twitter]",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "is_paid": True,
                    "is_ticketback": False
                })

    # remove duplicates
    unique_items = {i['title']:i for i in items}.values()
    final_list = list(unique_items)
    print(f"Found {len(final_list)} items from X (Twitter)")
    
    with open("twitter_latest.json", "w", encoding="utf-8") as f:
        json.dump(final_list[:10], f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_twitter_via_yahoo()
