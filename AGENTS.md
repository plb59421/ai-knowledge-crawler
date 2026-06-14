# ai_knowledge_crawler

AI 前沿知识爬虫，用于定时从多个 AI 技术信息渠道抓取内容，经过 AI 整理、中文标签、评分排序后写入本地知识库，并由 Web API 实时读库展示。

## Architecture

项目采用两层结构：

1. **AI 能力层**：`.ai/`
   - `prompts/`: 运行时提示词模板，例如 `summarize.st`
   - `skills/`: 项目级工作流说明，例如信息源接入、解析验证、知识整理
   - `knowledge/`: 来源画像、可信度规范、主题分类、安全规范
   - `automation.yaml`: 工具中立的自动化任务清单
2. **工程能力层**：`src/`
   - 爬虫、解析器、AI 分析、后处理、评分排序、存储、Web API

## Important Paths

```text
.ai/                         Tool-neutral AI project assets
config/settings.yaml          Non-secret defaults
config/user.example.yaml      Local configuration template
config/user.yaml              Local private config, ignored by Git
config/sources.yaml           Source definitions
src/                          Runtime source code
scripts/run_crawler.py        Manual crawl entry point
scripts/run_daily.py          Grouped scheduled crawl entry point
scripts/serve_api.py          Local report API entry point
scripts/export_automation.py  Export automation definitions
web/report/                   Vite + TypeScript report UI
knowledge_base/               Runtime knowledge base, ignored by Git
logs/                         Runtime logs, ignored by Git
```

## Runtime Flow

```text
scheduled crawler
  -> crawler / parser
  -> AI analysis
  -> auto-tag + rank
  -> KnowledgeStore
  -> FastAPI /api/report
  -> Web UI
```

Web access must read from `knowledge_base`; it must not call an LLM.

## Local Configuration

Copy the template and fill local-only values:

```powershell
Copy-Item config/user.example.yaml config/user.yaml
```

Never commit real API keys, tokens, cookies, logs, generated knowledge base data, `node_modules`, or build output.

## Automation

The canonical automation definition is `.ai/automation.yaml`.

Export it for external schedulers or AI tools:

```powershell
python scripts/export_automation.py --format json
python scripts/export_automation.py --format markdown
python scripts/export_automation.py --format cron
python scripts/export_automation.py --format windows
```

Daily crawler commands:

```powershell
python scripts/run_daily.py --group domestic --max-pages 5 --summarize
python scripts/run_daily.py --group proxy --max-pages 3 --summarize
```

## Validation

Run before committing:

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

## Change Guardrails

- Keep crawler and parser changes isolated per source.
- Prefer fixture tests over live network tests.
- Keep academic and general ranking profiles separate.
- Keep labels in Chinese or common AI abbreviations.
- Use `KnowledgeStore` as the write entry point for stored articles.
- Keep `.ai/` tool-neutral; do not put tool-specific secrets or generated runtime data there.
