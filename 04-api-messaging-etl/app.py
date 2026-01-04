# app.py
from flask import Flask, jsonify

app = Flask(__name__)

# "Database" of orders (static for lab)
ORDERS = [
    {"id": 1, "item": "Notebook", "qty": 2, "price_usd": 4.50},
    {"id": 2, "item": "Pencils",  "qty": 12, "price_usd": 3.20},
    {"id": 3, "item": "Backpack", "qty": 1, "price_usd": 29.99},
]

@app.get("/orders")
def get_orders():
    return jsonify({"orders": ORDERS})

if __name__ == "__main__":
    # Runs on http://127.0.0.1:5000
    app.run(debug=True)
