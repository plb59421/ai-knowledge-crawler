# AI Change Guide

Use this guide when asking an AI agent to modify the project.

## Common Tasks

### Add a new source

Touch points:

- `config/sources.yaml`
- `src/crawlers/<source>/crawler.py`
- `src/crawlers/<source>/parser.py`
- `src/crawlers/registry_config.py`
- `tests/fixtures/`
- `tests/test_parsers.py`

Acceptance:

- Parser works on fixture without network.
- `python scripts/run_crawler.py --source <source> --max-pages 1` returns clear stats.
- Source is assigned to the correct group in `scripts/run_daily.py`.

### Modify AI analysis

Touch points:

- `.ai/prompts/summarize.st`
- `src/ai/summarizer.py`
- `src/core/models.py` if schema changes are required
- `tests/test_ai_and_documents.py`

Acceptance:

- Invalid model output does not crash crawler.
- Existing articles are not re-analyzed unless `--force-analyze` is used.
- Analysis fields remain serializable through `Article.to_dict()`.

### Modify ranking or tags

Touch points:

- `src/ranking/tagger.py`
- `src/ranking/scorer.py`
- `src/ranking/freshness.py`
- `tests/test_ranking.py`

Acceptance:

- Academic and general content stay in separate ranking profiles.
- General freshness defaults to 30 days.
- Academic freshness defaults to 90 days.
- Labels remain Chinese or common AI abbreviations.

### Modify Web report

Touch points:

- `src/web_api/app.py`
- `src/ranking/report_data.py`
- `web/report/src/`
- `tests/test_web_api.py`
- `tests/test_report_frontend_source.py`

Acceptance:

- Frontend requests `/api/report` first.
- API reads `knowledge_base` on each request.
- No LLM call is made during Web access.

## Guardrails

- Do not commit `.env`, logs, generated knowledge base data, node_modules, or build outputs.
- Do not hard-code API keys.
- Keep crawler/parser/source-specific changes isolated.
- Prefer fixture tests over live network tests for CI-style verification.
- Run compile, pytest, and frontend build before release.
