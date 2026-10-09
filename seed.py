import sqlite3
from datetime import datetime, timezone

def run_seed():
    conn = sqlite3.connect("competitor_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            product_url TEXT NOT NULL UNIQUE,
            price_text TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            availability_text TEXT NOT NULL,
            rating_text TEXT,
            description TEXT,
            source_page TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        )
    """)

    sample_items = [
        ("A Light in the Attic", "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html", "£51.77", 51.77, "In stock (22 available)", "Three", "Poetry collection by Shel Silverstein."),
        ("Tipping the Velvet", "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html", "£53.74", 53.74, "In stock (20 available)", "One", "Historical fiction novel."),
        ("Soumission", "https://books.toscrape.com/catalogue/soumission_998/index.html", "£50.10", 50.10, "In stock (20 available)", "One", "Contemporary political satire."),
        ("Sharp Objects", "https://books.toscrape.com/catalogue/sharp-objects_997/index.html", "£47.82", 47.82, "In stock (20 available)", "Four", "Psychological mystery thriller."),
        ("Sapiens: A Brief History of Humankind", "https://books.toscrape.com/catalogue/sapiens_996/index.html", "£18.50", 18.50, "In stock (18 available)", "Five", "History of humankind by Yuval Noah Harari.")
    ]

    for item in sample_items:
        cursor.execute("""
            INSERT OR IGNORE INTO products (
                title, product_url, price_text, price_gbp, availability_text,
                rating_text, description, source_page, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'https://books.toscrape.com/catalogue/page-1.html', ?)
        """, (item[0], item[1], item[2], item[3], item[4], item[5], item[6], datetime.now(timezone.utc).isoformat()))

    conn.commit()
    conn.close()
    print("Database successfully seeded with 5 sample competitor products!")

if __name__ == "__main__":
    run_seed()
