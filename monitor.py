import json
import re
import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.oulim.kr/main.asp"

DISCORD = os.environ["DISCORD_WEBHOOK"]

KEYWORDS = [
    "콘래드",
    "Conrad",
]

html = requests.get(URL, timeout=20).text

soup = BeautifulSoup(html, "lxml")

target = None

for table in soup.find_all("table"):
    text = table.get_text(" ", strip=True)
    if "근무지" in text and "모집내용" in text:
        target = table
        break

if target is None:
    raise Exception("채용 테이블을 찾지 못했습니다.")

try:
    with open("state.json", "r", encoding="utf-8") as f:
        seen = set(json.load(f))
except:
    seen = set()

new_seen = set(seen)

for row in target.find_all("tr"):

    a = row.find("a", href=re.compile("work_total_view"))

    if not a:
        continue

    href = a["href"]

    m = re.search(r"num=(\d+)", href)

    if not m:
        continue

    num = m.group(1)

    if num in seen:
        continue

    tds = row.find_all("td")

    if len(tds) < 9:
        continue

    workplace = tds[2].get_text(" ", strip=True)

    if not any(k.lower() in workplace.lower() for k in KEYWORDS):
        continue

    content = tds[4].get_text(" ", strip=True)
    pay = tds[8].get_text(" ", strip=True)

    url = "https://www.oulim.kr" + href

    requests.post(
        DISCORD,
        json={
            "content":
f"""@everyone

📢 콘래드 공고 발견!

🏨 {workplace}

📄 {content}

💰 {pay}

🔗 {url}
"""
        },
        timeout=20,
    )

    new_seen.add(num)

with open("state.json", "w", encoding="utf-8") as f:
    json.dump(sorted(new_seen), f, ensure_ascii=False)
print("===== START =====")
print("HTML:", len(html))
print("State:", seen)
print("Webhook exists:", bool(DISCORD))
print("Discord:", r.status_code, r.text)
