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

Note: In environments without a running MySQL, the app will still start but first DB access will attempt to connect.
