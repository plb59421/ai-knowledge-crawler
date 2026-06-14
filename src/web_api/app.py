"""FastAPI app that reads the local knowledge base on each request."""

from typing import Literal

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.ranking.freshness import ACADEMIC_VALID_DAYS, GENERAL_VALID_DAYS
from src.ranking.report_data import ReportDataExporter
from src.storage.knowledge_store import KB_ROOT

app = FastAPI(title="AI Knowledge Crawler API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/report")
def report(
    profile: Literal["all", "general", "academic"] = "all",
    date: str | None = None,
    days: int | None = Query(default=None, ge=1),
    source: str | None = None,
    limit: int = Query(default=200, ge=1, le=1000),
    pass_score: float | None = None,
    include_expired: bool = False,
    general_valid_days: int = Query(default=GENERAL_VALID_DAYS, ge=1),
    academic_valid_days: int = Query(default=ACADEMIC_VALID_DAYS, ge=1),
    tag: str | None = None,
) -> dict:
    sources = [item.strip() for item in source.split(",") if item.strip()] if source else None
    return ReportDataExporter(KB_ROOT).build_payload(
        date=date,
        days=days,
        sources=sources,
        limit=limit,
        profile=profile,
        pass_score=pass_score,
        include_expired=include_expired,
        general_valid_days=general_valid_days,
        academic_valid_days=academic_valid_days,
        tag=tag,
    )
