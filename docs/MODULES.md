# Project Modules

This document defines module boundaries for future AI-assisted changes.

## AI Capability Layer

Location: `.ai/`

- `prompts/`: Runtime prompt templates. Current main template: `summarize.st`.
- `skills/`: Tool-neutral project workflows for source onboarding, parser validation, content summarization, and knowledge curation.
- `knowledge/`: Topic taxonomy, source trust policy, source profiles, and safety rules.
- `automation.yaml`: Canonical automation task definitions for scheduled ingestion and local report services.
- `PROJECT.md`: Rules for keeping this directory tool-neutral.

Constraints:

- Store no API keys, cookies, tokens, or private credentials.
- Keep tool-specific generated files outside `.ai/` unless they are regenerated from `automation.yaml`.
- Runtime secrets belong in `config/user.yaml`.

## Engineering Layer

Location: `src/`

- `core/`: `Article`, `CrawlResult`, registry, and shared exceptions.
- `crawlers/`: One directory per source, with crawler and parser implementations.
- `ai/`: OpenAI-compatible client, mock client, and structured summarizer.
- `processors/`: HTML, document, and article post-processing.
- `ranking/`: Chinese tags, profile-specific scoring, freshness filtering, and report payload construction.
- `storage/`: File knowledge base writes, deduplication, indexes, updates, and history.
- `utils/`: Configuration, logging, and proxy helpers.
- `web_api/`: FastAPI API that reads `knowledge_base` in real time.

Constraints:

- Crawlers fetch raw content; parsers convert raw content into `Article`.
- AI analysis runs during crawl jobs, not during Web access.
- `KnowledgeStore` is the write entry point for stored articles.
- Web API must reuse existing report query/export logic and avoid duplicate ranking rules.

## Entry Points

Location: `scripts/`

- `run_crawler.py`: Manual single-source or multi-source crawler.
- `run_daily.py`: Scheduled grouped crawler for `domestic`, `proxy`, or `all`.
- `serve_api.py`: Local FastAPI service.
- `generate_report.py`: Compatibility static report data export.
- `export_automation.py`: Converts `.ai/automation.yaml` to JSON, Markdown, cron, or Windows scheduler commands.
- `schedule_windows.ps1`: Legacy Windows Task Scheduler helper.
- `local_test.py`: Local fixture pipeline.

## Web Layer

Location: `web/report/`

- Vite + TypeScript report UI.
- Requests `/api/report` first.
- Static JSON fallback is only for offline preview.
- The UI shows two sections: `技术资讯` and `学术论文`.

## Runtime Data

Location: `knowledge_base/`

- `by_source/`: Primary article storage.
- `by_time/`: Time view.
- `by_topic/`: Topic view.
- `index/`: URL index, dedup records, and search indexes.
- `metadata/`: Crawl history and daily reports.
- `exports/`: Compatibility exports and frontend build output.

Runtime data is ignored by Git. Share stable examples through `tests/fixtures/`.
