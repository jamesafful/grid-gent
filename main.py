from __future__ import annotations
import os
from app.server import run_server

if __name__ == "__main__":
    port_str = os.environ.get("GRID_GENT_PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    run_server(port=port)
