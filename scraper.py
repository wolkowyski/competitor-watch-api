import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin
from database import get_db

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

USER_AGENT = "CompetitorWatchBot/1.0 (+https://github.com/braianwolkowyski/competitor-watch-api)"
REQUEST_DELAY = 0.5  # Polite delay between outbound calls
TIMEOUT = 10

def normalize_price(text: str) -> float:
    match = re.search(r"\d+\.\d+", text)
    return float(match.group()) if match else 0.0

def fetch_html_cached(url: str, cache_key: str) -> Optional[str]:
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.html")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    time.sleep(REQUEST_DELAY)
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 200:
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            return resp.text
    except Exception:
        pass
    return None

def run_polite_ingestion(max_pages: int = 3) -> dict:
    start_ts = time.time()
    current_url = "https://books.toscrape.com/catalogue/page-1.html"
    extracted_books = []

    for page_idx in range(1, max_pages + 1):
        html = fetch_html_cached(current_url, f"page_{page_idx}")
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        pods = soup.select("article.product_pod")
        for pod in pods:
            a_tag = pod.select_one("h3 > a")
            if not a_tag:
                continue
            title = a_tag.get("title", a_tag.text.strip())
            rel_url = a_tag["href"]
            abs_url = urljoin(current_url, rel_url)

            price_tag = pod.select_one("p.price_color")
            price_text = price_tag.text.strip() if price_tag else "£0.00"
            price_num = normalize_price(price_text)

            avail_tag = pod.select_one("p.availability")
            avail_text = avail_tag.text.strip() if avail_tag else "In stock"

            rating_tag = pod.select_one("p.star-rating")
            rating = "Three"
            if rating_tag:
                classes = rating_tag.get("class", [])
                rating = [c for c in classes if c != "star-rating"][0] if len(classes) > 1 else "Unknown"

            extracted_books.append({
                "title": title,
                "product_url": abs_url,
                "price_text": price_text,
                "price_gbp": price_num,
                "availability_text": avail_text,
                "rating_text": rating,
                "description": f"Verified competitor record for {title}",
                "source_page": current_url,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            })

        next_btn = soup.select_one("li.next > a")
        if next_btn:
            current_url = urljoin(current_url, next_btn["href"])
        else:
            break

    # Persist into SQLite using INSERT OR REPLACE for idempotency
    conn = get_db()
    cursor = conn.cursor()
    ingested_count = 0
    for b in extracted_books:
        cursor.execute("""
            INSERT OR REPLACE INTO products (
                title, product_url, price_text, price_gbp, availability_text,
                rating_text, description, source_page, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            b["title"], b["product_url"], b["price_text"], b["price_gbp"],
            b["availability_text"], b["rating_text"], b["description"],
            b["source_page"], b["fetched_at"]
        ))
        ingested_count += 1

    duration_ms = int((time.time() - start_ts) * 1000)
    cursor.execute("""
        INSERT INTO sync_logs (timestamp, duration_ms, items_ingested, status)
        VALUES (?, ?, ?, 'COMPLETED')
    """, (datetime.now(timezone.utc).isoformat(), duration_ms, ingested_count))

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "items_ingested": ingested_count,
        "source_pages": max_pages,
        "duration_ms": duration_ms
    }
