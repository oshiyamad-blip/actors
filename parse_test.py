import re
from bs4 import BeautifulSoup
with open('sample.html', 'r', encoding='utf-8') as f:
    html = f.read()
soup = BeautifulSoup(html, 'html.parser')

items = soup.find_all('div', class_='articleWrap')
if not items:
    items = soup.find_all('article')
if not items:
    items = soup.find_all('div', class_=re.compile('article.*|post.*'))

print(f"Found {len(items)} items")

for i, item in enumerate(items[:3]):
    text = item.text.strip().replace('\n', ' ')
    print(f"[{i}] {text[:150]}")
