"""
Entrypoint for running the FastAPI app with Uvicorn.

Usage:
    python -m src.api
or
    uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
"""

import os
from uvicorn import run


def _get_port() -> int:
    # Allow override through env; default to 3001 as specified by work item
    try:
        return int(os.getenv("PORT", "3001"))
    except ValueError:
        return 3001


# PUBLIC_INTERFACE
def main() -> None:
    """Start the Uvicorn server serving the FastAPI app.

    Uses environment variables:
    - PORT: port to bind (default 3001)
    - HOST: host/interface to bind (default 0.0.0.0)
    """
    host = os.getenv("HOST", "0.0.0.0")
    port = _get_port()
    # Reload only if explicitly set; default false in container/CI
    reload_flag = os.getenv("RELOAD", "false").lower() == "true"
    run("src.api.main:app", host=host, port=port, reload=reload_flag, factory=False)


if __name__ == "__main__":
    main()
