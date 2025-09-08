import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import openapi_tags
from src.core.database import init_db
from src.routers import auth, products, users, orders

# Initialize FastAPI app with metadata for Swagger/OpenAPI
app = FastAPI(
    title="Gadget Store Backend API",
    description="RESTful API for an e-commerce gadget store. Provides authentication, product management, and orders.",
    version="1.0.0",
    contact={"name": "Gadget Store", "email": "support@gadgetstore.local"},
    openapi_tags=openapi_tags,
)

# CORS configuration using environment variable or default to '*'
allowed_origins: List[str] = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")] if os.getenv("CORS_ALLOW_ORIGINS") else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    """
    Application startup hook.

    Initializes the database and ensures connection can be established.
    """
    await init_db()


# Health check
@app.get("/", summary="Health Check", tags=["System"])
def health_check():
    """
    Returns a simple health response to verify the API is running.

    Returns:
        dict: A message indicating the service status.
    """
    return {"message": "Healthy"}


# Register routers
app.include_router(auth.router, prefix="/auth")
app.include_router(products.router, prefix="/products")
app.include_router(users.router, prefix="/users")
app.include_router(orders.router, prefix="/orders")
