# CompetitorWatch API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **FlyRank Backend AI Engineering Track — Capstone Project: Your 10x Solution**  
> *Author: Braian Wolkowyski*

---

## 1. Problem Statement & The 10x Claim

### The Problem
E-commerce sellers waste 3-4 hours every week manually checking competitor websites, copying changing prices into fragile spreadsheets, and verifying stock status by hand to protect sales margins. This manual work is slow, error-prone, and cannot scale past a handful of items.

### The 10x Claim
**CompetitorWatch API** replaces a 3-hour manual auditing chore with a single authenticated API call that ingests, validates, caches, and indexes 60 competitor catalog items in **under 3 seconds** — delivering a 60x speed improvement at $0 operational cost.

---

## 2. Program Concepts Implemented (5 Core Concepts)

| # | Concept | Implementation in Code |
|---|---|---|
| 1 | **API Endpoints** | REST routes (`/catalog/sync`, `/catalog/products`, `/health`) with status codes (200, 201, 400, 401, 404), Pydantic schemas, and Swagger UI at `/docs`. |
| 2 | **Database Persistence** | Persistent SQLite storage (`competitor_data.db`) storing products and sync audit logs surviving server reboots. |
| 3 | **Authentication** | Bearer JWT security scheme via FastAPI `Depends(verify_jwt_token)` protecting catalog ingestion and deletion routes. |
| 4 | **Two-Tier Caching** | Local disk caching (`cache/*.html`) dropping repeated outbound query times from ~2.8s to under 5ms. |
| 5 | **Web Scraping Pipeline (Swap 1)** | Polite external crawler parsing 60 products across 3 catalogue pages with 500ms delay and User-Agent identification. |

*Swap Justification:* Background Jobs swapped for Web Scraping Pipeline because the core architectural value is transforming external web data into structured relational schemas on demand.

---

## 3. Five-Minute Demo Path (Quick Start)

### Installation
```bash
# 1. Clone repository
git clone https://github.com/braianwolkowyski/competitor-watch-api.git
cd competitor-watch-api

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env from example
cp .env.example .env

# 4. Start the server
uvicorn main:app --reload --port 8000
```

Interactive documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

### Step-by-Step Verification with curl

#### Step 1: Health Check
```bash
curl -i http://localhost:8000/health
```
```http
HTTP/1.1 200 OK
{"status":"healthy","database":"connected"}
```

#### Step 2: Test Authentication Barrier (Unauthorized)
```bash
curl -i -X POST http://localhost:8000/catalog/sync
```
```http
HTTP/1.1 401 Unauthorized
{"detail":{"error":"Authorization Bearer token required"}}
```

#### Step 3: Trigger Ingestion with Bearer Token
```bash
curl -i -X POST http://localhost:8000/catalog/sync   -H "Authorization: Bearer secret_demo_jwt_token_2026"
```
```http
HTTP/1.1 201 Created
{"status":"success","items_ingested":60,"source_pages":3,"duration_ms":2840}
```

#### Step 4: Query Catalog with Price Filter
```bash
curl -s "http://localhost:8000/catalog/products?max_price=20.0"
```

#### Step 5: Test Persistence Across Restart
Kill the server (`Ctrl + C`), restart it, and query product #1:
```bash
curl -i http://localhost:8000/catalog/products/1
```
The data is preserved in SQLite across restarts.

---

## 4. Instant Seed Script (Alternative)
To query the database without running network ingestion:
```bash
python seed.py
```

---

## 5. Security & Architecture
- **Zero Secrets in Git:** Sensitive tokens live strictly in `.env` (gitignored). `.env.example` committed.
- **Polite Bot Behavior:** Respects external sites using `CompetitorWatchBot/1.0` headers and 500ms throttling.
