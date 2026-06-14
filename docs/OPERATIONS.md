# Operations Guide

## Environment

Python:

```powershell
python -m pip install -r requirements.txt
```

Frontend:

```powershell
cd web/report
npm install
```

LLM:

```powershell
$env:DASHSCOPE_API_KEY="your_dashscope_api_key"
$env:OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL="qwen-plus"
```

Never commit real API keys.

## Daily Run

Domestic/no-proxy sources:

```powershell
python scripts/run_daily.py --group domestic --max-pages 5 --summarize --analysis-limit 10
```

Proxy sources:

```powershell
python scripts/run_daily.py --group proxy --max-pages 3 --summarize --analysis-limit 10
```

All default sources:

```powershell
python scripts/run_daily.py --group all --max-pages 5 --summarize --analysis-limit 10
```

Notes:

- `--summarize` enables real LLM calls.
- `--analysis-limit` caps AI calls per source run.
- Existing articles are skipped by default.
- `--force-analyze` updates existing records, useful for backfill.

## Web Runtime

Start API:

```powershell
python scripts/serve_api.py --host 127.0.0.1 --port 8000
```

Start frontend:

```powershell
cd web/report
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

API examples:

```text
GET http://127.0.0.1:8000/api/health
GET http://127.0.0.1:8000/api/report
GET http://127.0.0.1:8000/api/report?profile=academic&limit=50
GET http://127.0.0.1:8000/api/report?tag=LLM&pass_score=0
```

## Release Checklist

Run before pushing:

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

Also verify:

- `git status --short` has no generated runtime data accidentally staged.
- Run a secret scan for provider key prefixes and environment assignments; it should return no real key.
- `python scripts/run_crawler.py --list` lists registered sources.

## Known Runtime Notes

- Some international sources require a local proxy.
- Scrapling may print proxy configuration deprecation warnings; this does not block current runs.
- ArXiv PDF extraction can fail for some papers; parser falls back to API metadata and summary.
- `report_latest.json` is compatibility output, not the primary Web data path.
