from fastapi import FastAPI
from app.config import settings
from app.api import customers, orders

app = FastAPI(
    title="RetailCRM",
    description="FastAPI application for RetailCRM integration",
    version="1.0.0",
    debug=settings.debug
)

app.include_router(customers.router, prefix="/api/v1", tags=["Customers"])
app.include_router(orders.router, prefix="/api/v1", tags=["Orders"])


@app.get("/")
async def root():
    return {
        "message": "RetailCRM API Integration",
        "docs": "/docs",
        "health": "ok"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}