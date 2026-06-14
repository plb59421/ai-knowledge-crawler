"""Serve the local knowledge-base API."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn

from src.utils.config_loader import get_runtime_config


def main():
    runtime_config = get_runtime_config()
    parser = argparse.ArgumentParser(description="Serve AI knowledge crawler API")
    parser.add_argument("--host", default=runtime_config.get("api_host", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(runtime_config.get("api_port", 8000)))
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run("src.web_api.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
