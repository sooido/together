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

print("===== START =====")

# 사이트 접속
html = requests.get(URL, timeout=20).text
print("HTML Length:", len(html))

soup = BeautifulSoup(html, "lxml")

# 채용 테이블 찾기
target = None

for table in soup.find_all("table"):
    text = table.get_text(" ", strip=True)
    if "근무지" in text and "모집내용" in text:
        target = table
        break

if target is None:
    raise Exception("채용 테이블을 찾지 못했습니다.")

print("채용 테이블 발견")

# 이전 상태 읽기
try:
    with open("state.json", "r", encoding="utf-8") as f:
        seen = set(json.load(f))
except Exception:
    seen = set()

print("기존 state:", seen)
print("Webhook exists:", bool(DISCORD))

new_seen = set(seen)

# 공고 확인
for row in target.find_all("tr"):

    a = row.find("a", href=re.compile("work_total_view"))

    if not a:
        continue

    href = a["href"]

    m = re.search(r"num=(\d+)", href)

    if not m:
        continue

    num = m.group(1)

    tds = row.find_all("td")

    if len(tds) < 9:
        continue

    workplace = tds[2].get_text(" ", strip=True)

    print("--------------------------")
    print("공고번호:", num)
    print("근무지:", workplace)

    if num in seen:
        print("이미 확인한 공고 -> 건너뜀")
        continue

    if not any(k.lower() in workplace.lower() for k in KEYWORDS):
        print("키워드 불일치 -> 건너뜀")
        continue

    content = tds[4].get_text(" ", strip=True)
    pay = tds[8].get_text(" ", strip=True)

    url = "https://www.oulim.kr" + href

    print("새 콘래드 공고 발견!")
    print(content)

    r = requests.post(
        DISCORD,
        json={
            "content": f"""@everyone

📢 콘래드 공고 발견!

🏨 {workplace}

📄 {content}

💰 {pay}

🔗 {url}
"""
        },
        timeout=20,
    )

    print("Discord Status:", r.status_code)
    print("Discord Response:", r.text)

    new_seen.add(num)

# 상태 저장
with open("state.json", "w", encoding="utf-8") as f:
    json.dump(sorted(new_seen), f, ensure_ascii=False)

print("저장 완료")
print("===== END =====")
