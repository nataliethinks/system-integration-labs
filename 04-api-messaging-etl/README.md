# API Integration, Messaging & ETL Pipeline

## Overview
This project demonstrates an **end-to-end system integration scenario** combining synchronous APIs, asynchronous messaging, and a simple ETL pipeline.

It simulates how enterprise systems exchange transactional data using **REST APIs**, **message queues**, and **data transformation workflows**, a common pattern in ERP, order management, and integration platforms.


## Architecture
The integration flow follows this sequence:

1. A REST API exposes order data in JSON format  
2. API responses are published to a message queue  
3. A consumer service processes messages asynchronously  
4. An ETL pipeline transforms and persists the data  

**Integration Pattern:**  
- Point-to-point (API)  
- Asynchronous messaging (decoupling producer and consumer)  
- ETL-style data processing  


## Tech Stack

**Language:** Python  
**API:** Flask (REST)  
**Messaging:** RabbitMQ  
**Data Processing:** Python ETL script  
**Storage:** SQLite  
**Data Format:** JSON  


## Components

### 1. REST API (Producer)
Exposes an `/orders` endpoint returning order data in JSON
Represents a transactional source system (e.g., e-commerce or ERP)

Example response:
```json
{
  "order_id": 1001,
  "item": "Laptop",
  "price_usd": 1200
}
