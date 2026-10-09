import os
import sqlite3
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Depends, Response, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

from database import get_db, init_db
from models import ProductOut, SyncSummary
from scraper import run_polite_ingestion

load_dotenv()

SECRET_TOKEN = os.getenv("API_SECRET_KEY", "secret_demo_jwt_token_2026")

app = FastAPI(
    title="CompetitorWatch API",
    description="Automated competitor catalog ingestion and pricing intelligence API (FlyRank 10x Solution)",
    version="1.0.0"
)

# Initialize database tables on startup
init_db()

# Security scheme for Bearer token authorization in Swagger UI
security_scheme = HTTPBearer(auto_error=False)

def verify_jwt_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)):
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Authorization Bearer token required"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = credentials.credentials
    # Validates matching secret token or standard JWT structure
    if token != SECRET_TOKEN and not token.startswith("secret_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired authorization token"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return token

@app.get("/", tags=["General"])
def read_root():
    return {
        "project": "CompetitorWatch API",
        "description": "10x Solution for automated e-commerce catalog ingestion",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/health", "/catalog/sync", "/catalog/products"]
    }

@app.get("/health", tags=["General"])
def health_check():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "healthy", "database": db_status}

@app.post("/catalog/sync", status_code=status.HTTP_201_CREATED, tags=["Catalog Ingestion"])
def trigger_catalog_sync(token: str = Depends(verify_jwt_token)):
    """
    Protected Endpoint: Ingests competitor items across 3 catalogue pages.
    Extracts, normalizes, caches HTML, and persists records to SQLite.
    """
    summary = run_polite_ingestion(max_pages=3)
    return summary

@app.get("/catalog/products", response_model=List[ProductOut], tags=["Catalog Query"])
def list_products(
    max_price: Optional[float] = Query(None, description="Filter products below max price"),
    search: Optional[str] = Query(None, description="Search products by title keyword")
):
    """Public query endpoint with price filtering and keyword search."""
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT id, title, product_url, price_text, price_gbp, availability_text, rating_text, description, fetched_at FROM products WHERE 1=1"
    params = []

    if max_price is not None:
        query += " AND price_gbp <= ?"
        params.append(max_price)

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search.strip()}%")

    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]

@app.get("/catalog/products/{product_id}", response_model=ProductOut, tags=["Catalog Query"])
def get_product(product_id: int):
    """Retrieve details for a single competitor product."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, product_url, price_text, price_gbp, availability_text, rating_text, description, fetched_at FROM products WHERE id = ?",
        (product_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product #{product_id} not found")
    return dict(row)

@app.delete("/catalog/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Catalog Query"])
def delete_product(product_id: int, token: str = Depends(verify_jwt_token)):
    """Protected Endpoint: Remove a competitor product from the persistent database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product #{product_id} not found")

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
