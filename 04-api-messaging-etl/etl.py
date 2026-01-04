# etl.py
import os
import time
import sqlite3
import requests
from datetime import datetime, timezone

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/orders")
DB_PATH = os.getenv("DB_PATH", "orders.db")
USD_TO_EUR = float(os.getenv("USD_TO_EUR", "0.92"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY,
  item TEXT NOT NULL,
  qty INTEGER NOT NULL,
  price_usd REAL NOT NULL,
  price_eur REAL NOT NULL,
  inserted_at TEXT NOT NULL
);
"""

def extract():
    resp = requests.get(API_URL, timeout=5)
    resp.raise_for_status()
    return resp.json()["orders"]

def transform(rows):
    out = []
    for r in rows:
        price_eur = round(r["price_usd"] * USD_TO_EUR, 2)
        out.append({
            "id": r["id"],
            "item": r["item"],
            "qty": r["qty"],
            "price_usd": r["price_usd"],
            "price_eur": price_eur,
            "inserted_at": datetime.now(timezone.utc).isoformat()
        })
    return out

def load(rows):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(SCHEMA)

    # Upsert on primary key (id); replace for simplicity
    cur.executemany(
        """
        INSERT INTO orders (id, item, qty, price_usd, price_eur, inserted_at)
        VALUES (:id, :item, :qty, :price_usd, :price_eur, :inserted_at)
        ON CONFLICT(id) DO UPDATE SET
          item=excluded.item,
          qty=excluded.qty,
          price_usd=excluded.price_usd,
          price_eur=excluded.price_eur,
          inserted_at=excluded.inserted_at
        """,
        rows,
    )
    conn.commit()
    conn.close()
    return len(rows)

def main():
    raw = extract()
    xformed = transform(raw)
    n = load(xformed)
    print(f"ETL complete. Loaded {n} rows into {DB_PATH}.")

if __name__ == "__main__":
    main()
