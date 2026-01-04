# publish_orders.py
import json
import os
import pika
import requests

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = os.getenv("QUEUE_NAME", "orders")
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/orders")

def main():
    # 1) Fetch from REST API
    resp = requests.get(API_URL, timeout=5)
    resp.raise_for_status()
    payload = resp.json()  # {"orders": [...]}

    # 2) Connect to RabbitMQ
    params = pika.ConnectionParameters(host=RABBITMQ_HOST)
    conn = pika.BlockingConnection(params)
    channel = conn.channel()

    # 3) Declare queue (idempotent)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # 4) Publish message (persisted)
    body = json.dumps(payload)
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=body.encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=2  # make message persistent
        ),
    )
    print(f"Published {len(payload.get('orders', []))} orders to queue '{QUEUE_NAME}'.")
    conn.close()

if __name__ == "__main__":
    main()
