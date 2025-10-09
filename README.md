# 🧩 Zenskar Two-Way Customer Sync

A **two-way synchronization system** between a local **customer catalog** and **Stripe’s customer system**, using:

* 🐍 **FastAPI** (Python 3.13)
* 🧭 **PostgreSQL** (local relational DB)
* 📨 **Kafka** (event bus for async sync)
* 💳 **Stripe API** (external service)
* 🐳 **Docker Compose** (for Kafka + Zookeeper)

The system ensures that any customer **added, updated, or deleted** in either system reflects in the other **within seconds** — enabling **real-time, event-driven sync**.

---

## ⚙️ Tech Stack

| Layer             | Technology     |
| ----------------- | -------------- |
| API Framework     | FastAPI        |
| Database          | PostgreSQL     |
| Messaging Queue   | Apache Kafka   |
| ORM               | SQLAlchemy     |
| External Service  | Stripe         |
| Deployment        | Docker Compose |
| Schema Validation | Pydantic v2    |

---

## 🏗️ Architecture Overview

```
           +----------------------+
           |     FastAPI App      |
           |   (Local Catalog)    |
           +----------+-----------+
                      |
                      |  REST API / Webhook
                      ↓
           +----------------------+
           |      Stripe API      |
           | (External Catalog)   |
           +----------+-----------+
                      |
                      |  JSON Events via Kafka
                      ↓
           +----------------------+
           |       Kafka Bus      |
           | (customer_events)    |
           +----------+-----------+
                      |
                      ↓
           +----------------------+
           |   Kafka Consumer     |
           | (Worker Thread)      |
           +----------------------+
```

---

## 🧰 Features

✅ CRUD APIs for Local Customers
✅ Real-time Stripe Webhook Integration
✅ Event-Driven Kafka Communication
✅ Threaded Consumer for Async Sync
✅ Custom Exception Handling
✅ Scalable, Modular Codebase

---

## 🗂 Project Structure

```
app/
├── api/
│   └── v1/
│       ├── customers.py          # Local CRUD routes
│       ├── stripe_webhook.py     # Stripe webhook handler
│       └── routes.py             # Route aggregator
│
├── core/
│   └── settings.py               # Environment configuration
|   └── exceptions.py             # all type of error handling/exceptional handling
│
├── crud/
│   └── customer.py               # DB operations + Kafka publishing
│
├── db/
│   ├── base.py                   # SQLAlchemy setup
|
│── models/
|  ├──customer.py                 # Customer model
|
|
│── schemas/
|  ├──customer.py                 # Customer schema
│
├── integrations/
│   ├── stripe_integration.py     # Stripe API service
│   ├── producer.py               # Kafka producer
│   └── consumer.py               # Kafka consumer
│
└── main.py                       # App entry point
```

---

## ⚙️ Local Setup Guide

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/<your-username>/customer-sync-service.git
cd customer-sync-service
```

### 2️⃣ Create a Virtual Environment

```bash
python3 -m venv zenskarenv
source zenskarenv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup PostgreSQL

In your psql shell:

```sql
CREATE DATABASE zenskar;
CREATE USER ehtisham WITH PASSWORD '123456';
GRANT ALL PRIVILEGES ON DATABASE zenskar TO ehtisham;
```

Update `.env` file:

```env
DATABASE_URL=postgresql://ehtisham:123456@localhost:5432/zenskar
STRIPE_SECRET_KEY=sk_test_***
STRIPE_WEBHOOK_SECRET=whsec_***
KAFKA_BROKER_URL=localhost:9092
KAFKA_CUSTOMER_TOPIC=customer_events
```

---

## 🐳 Start Kafka & Zookeeper

```bash
docker compose up -d
docker ps
```

Your output should show:

```
zookeeper  → 2181
kafka      → 9092
```

---

## ▶️ Run the App

```bash
uvicorn app.main:app --reload
```

Then open the docs:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🔄 Data Sync Flow

### **Local → Stripe**

1. CRUD API updates local DB
2. Kafka producer publishes event
3. Kafka consumer pushes changes to Stripe

### **Stripe → Local**

1. Stripe webhook triggers FastAPI route
2. Event published to Kafka
3. Consumer updates local DB

---

## 🧩 Example Events

| Event Type         | Direction      | Description                   |
| ------------------ | -------------- | ----------------------------- |
| `customer.created` | Local → Stripe | New customer created locally  |
| `customer.updated` | Both           | Update on either system       |
| `customer.deleted` | Both           | Deletion propagated both ways |

---

## 🧠 Design Highlights

* **Event-Driven Architecture** → No direct blocking API calls
* **Kafka decouples systems** → Extensible and resilient
* **Custom error classes** → Clean error handling
* **Threaded consumer** → Real-time updates
* **Separation of concerns** → Independent integration layers

---


## 🧪 Test Webhooks

Expose FastAPI via **ngrok**:

```bash
ngrok http 8000
```

Use the generated URL in Stripe Dashboard →
**Developers → Webhooks → Add Endpoint**

Example:

```
https://<your-id>.ngrok.io/api/v1/stripe/webhook
```

---
