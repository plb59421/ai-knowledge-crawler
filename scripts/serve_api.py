"""Serve the local knowledge-base API."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Serve AI knowledge crawler API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run("src.web_api.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
