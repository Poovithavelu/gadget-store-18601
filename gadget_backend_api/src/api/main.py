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

# CORS configuration using environment variable or default to known dev preview origin.
# If CORS_ALLOW_ORIGINS is not set, explicitly list the common React dev URL to allow credentialed requests.
_default_dev_origin = "https://vscode-internal-18322-qa.qa01.cloud.kavia.ai:3000"
if os.getenv("CORS_ALLOW_ORIGINS"):
    allowed_origins: List[str] = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if o.strip()]
else:
    allowed_origins = [_default_dev_origin]

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

    Initializes the database (non-fatal). If the database is unavailable, the API will still start,
    and DB-dependent routes may fail until the DB is reachable.
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


# Make OpenAPI generation resilient; if something goes wrong, do not 500.
def custom_openapi():
    """
    Generate OpenAPI schema; if generation fails, return a minimal schema to avoid 500 on /openapi.json.
    """
    if app.openapi_schema:
        return app.openapi_schema
    try:
        app.openapi_schema = app.openapi()
        return app.openapi_schema
    except Exception as exc:
        # Fallback minimal schema to ensure docs endpoint doesn't 500.
        print(f"[openapi][warning] Failed to generate OpenAPI schema: {exc}")
        return {
            "openapi": "3.1.0",
            "info": {"title": app.title, "version": app.version, "description": "Fallback schema due to generation error"},
            "paths": {},
        }


# Assign the custom generator
app.openapi = custom_openapi  # type: ignore
