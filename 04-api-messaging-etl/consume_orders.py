# consume_orders.py
import json
import os
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = os.getenv("QUEUE_NAME", "orders")

def handle_message(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))
    print("Received message from queue:")
    print(json.dumps(data, indent=2))
    # Acknowledge AFTER successful processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    params = pika.ConnectionParameters(host=RABBITMQ_HOST)
    conn = pika.BlockingConnection(params)
    channel = conn.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Fair dispatch: prefetch 1
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)

    print(f"Waiting for messages on '{QUEUE_NAME}'. Press Ctrl+C to exit.")
    channel.start_consuming()

if __name__ == "__main__":
    main()
