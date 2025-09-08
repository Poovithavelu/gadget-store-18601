import os
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# CORS configuration
# Reads CORS_ALLOW_ORIGINS from env as a comma-separated list. Supports "*" to allow all origins (non-credentialed).
# If not specified, we default to common React dev origins and the known preview origin to avoid "failed to fetch" during signup.
_default_dev_origins: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
    # Local preview and HTTPS dev proxies that may be used by the environment
    "https://vscode-internal-18322-qa.qa01.cloud.kavia.ai:3000",
    "https://vscode-internal-18322-qa.qa01.cloud.kavia.ai",
    "http://localhost",
    "http://127.0.0.1",
]
env_cors = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
if env_cors:
    env_list = [o.strip() for o in env_cors.split(",") if o.strip()]
    wildcard = any(o == "*" for o in env_list)
    if wildcard:
        # With wildcard, browsers disallow credentials. We disable credentials in this mode.
        allowed_origins: List[str] = ["*"]
        allow_credentials = False
    else:
        allowed_origins = env_list
        allow_credentials = True
else:
    # Sensible defaults for dev to prevent CORS issues between frontend (3000) and backend (3001)
    allowed_origins = _default_dev_origins
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
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

# PUBLIC_INTERFACE
@app.get(
    "/_cors_info",
    summary="CORS Info",
    description="Debug endpoint that returns the current CORS configuration.",
    tags=["System"],
)
def cors_info():
    """
    Returns the current CORS settings. Useful for debugging 'failed to fetch' issues.
    """
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": allow_credentials,
        "note": "Set CORS_ALLOW_ORIGINS env (comma-separated) to override. Use '*' to allow all (credentials disabled).",
    }


# PUBLIC_INTERFACE
@app.get(
    "/api-info",
    summary="API Info",
    description="Returns API metadata helpful for frontends (CORS and version).",
    tags=["System"],
)
def api_info():
    """
    Returns metadata useful for frontends to diagnose connectivity.
    """
    return {
        "name": "Gadget Store Backend API",
        "version": app.version,
        "cors": {"allow_origins": allowed_origins, "allow_credentials": allow_credentials},
    }

# Register routers
app.include_router(auth.router, prefix="/auth")
app.include_router(products.router, prefix="/products")
app.include_router(users.router, prefix="/users")
app.include_router(orders.router, prefix="/orders")

# Global user-friendly error handling for DB initialization/runtime issues
@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    # If the error looks like DB not initialized, map to 503 with friendly payload.
    msg = str(exc)
    if "Database is not initialized" in msg:
        return JSONResponse(
            status_code=503,
            content={"detail": {"message": "Service temporarily unavailable", "code": "DB_UNAVAILABLE", "details": msg}},
        )
    # Fallback generic 500
    return JSONResponse(status_code=500, content={"detail": {"message": "Internal server error"}})


# Make OpenAPI generation resilient; if something goes wrong, do not 500.
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    """
    Generate OpenAPI schema safely using FastAPI's get_openapi to avoid recursion.
    On error, return a minimal fallback schema so /openapi.json does not 500.
    """
    if getattr(app, "openapi_schema", None):
        return app.openapi_schema
    try:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=openapi_tags,
        )
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
