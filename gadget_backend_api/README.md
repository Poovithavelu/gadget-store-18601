# Gadget Store Backend API

FastAPI backend service for the Gadget Store sample app.

How to run locally:
- Install dependencies:
  pip install -r requirements.txt
- Start the server:
  uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

Environment variables (configure in .env; do not commit real secrets):
- PORT: default 3001
- HOST: default 0.0.0.0
- CORS_ALLOW_ORIGINS: comma-separated list of allowed origins (e.g., http://localhost:3000)
- JWT_SECRET_KEY: required for secure auth
- MYSQL_URL or MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

See .env.example for a sample configuration.

Notes on frontend "Failed to fetch":
- Ensure CORS allows your frontend origin. You can verify with GET /_cors_info.
- Ensure the backend is reachable at the URL the frontend uses (e.g., http://localhost:3001 or the provided preview URL).
- If the database is not available, GET /products now returns 503 with a friendly JSON payload instead of 500. Frontends should display the message rather than reporting a network error.

Debug endpoints:
- GET /              Health check
- GET /_cors_info    Current CORS settings
- GET /api-info      API name/version and CORS summary
