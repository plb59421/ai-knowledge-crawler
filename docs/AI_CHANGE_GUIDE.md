# AI Change Guide

[中文](#中文) | [English](#english)

---

## 中文

当你要求 AI 工具修改项目时，优先参考本指南。

### 新增信息源

修改点：

- `config/sources.yaml`
- `src/crawlers/<source>/crawler.py`
- `src/crawlers/<source>/parser.py`
- `src/crawlers/registry_config.py`
- `tests/fixtures/`
- `tests/test_parsers.py`

验收标准：

- parser 可以在离线 fixture 上运行。
- `python scripts/run_crawler.py --source <source> --max-pages 1` 返回清晰统计。
- 新源被加入 `scripts/run_daily.py` 中正确的默认分组。

### 修改 AI 分析

修改点：

- `.ai/prompts/summarize.st`
- `src/ai/summarizer.py`
- `src/core/models.py`
- `tests/test_ai_and_documents.py`

验收标准：

- 非法模型输出不会导致爬虫崩溃。
- 已存在文章不会重复分析，除非使用 `--force-analyze`。
- 分析字段可以通过 `Article.to_dict()` 序列化。

### 修改标签或评分

修改点：

- `src/ranking/tagger.py`
- `src/ranking/scorer.py`
- `src/ranking/freshness.py`
- `tests/test_ranking.py`

验收标准：

- 学术论文和技术资讯保持独立评分体系。
- 技术资讯默认时效为 30 天。
- 学术论文默认时效为 90 天。
- 标签保持中文或常见 AI 缩写。

### 修改 Web 报告

修改点：

- `src/web_api/app.py`
- `src/ranking/report_data.py`
- `web/report/src/`
- `tests/test_web_api.py`
- `tests/test_report_frontend_source.py`

验收标准：

- 前端优先请求 `/api/report`。
- API 每次请求实时读取 `knowledge_base`。
- Web 访问不触发 LLM 调用。

### 修改自动化调度

修改点：

- `.ai/automation.yaml`
- `scripts/export_automation.py`
- `tests/test_automation_export.py`

验收标准：

- `python scripts/export_automation.py --format json` 成功。
- cron 和 Windows 导出包含预期任务。
- 自动化任务不包含真实密钥。

### 通用保护规则

- 不提交 `.env`、`config/user.yaml`、日志、运行时知识库、`node_modules` 或构建产物。
- 不硬编码 API Key。
- 爬虫和解析器改动应按信息源隔离。
- CI 风格验证优先使用 fixture 测试，不依赖真实网络。
- 发布前运行编译、测试和前端构建。

---

## English

Use this guide when asking an AI tool to modify the project.

### Add a New Source

Touch points:

- `config/sources.yaml`
- `src/crawlers/<source>/crawler.py`
- `src/crawlers/<source>/parser.py`
- `src/crawlers/registry_config.py`
- `tests/fixtures/`
- `tests/test_parsers.py`

Acceptance:

- Parser works on an offline fixture.
- `python scripts/run_crawler.py --source <source> --max-pages 1` returns clear stats.
- The new source is assigned to the correct default group in `scripts/run_daily.py`.

### Modify AI Analysis

Touch points:

- `.ai/prompts/summarize.st`
- `src/ai/summarizer.py`
- `src/core/models.py`
- `tests/test_ai_and_documents.py`

Acceptance:

- Invalid model output does not crash the crawler.
- Existing articles are not re-analyzed unless `--force-analyze` is used.
- Analysis fields remain serializable through `Article.to_dict()`.

### Modify Tags or Ranking

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

### Modify Web Report

Touch points:

- `src/web_api/app.py`
- `src/ranking/report_data.py`
- `web/report/src/`
- `tests/test_web_api.py`
- `tests/test_report_frontend_source.py`

Acceptance:

- Frontend requests `/api/report` first.
- API reads `knowledge_base` on each request.
- Web access does not invoke an LLM.

### Modify Automation

Touch points:

- `.ai/automation.yaml`
- `scripts/export_automation.py`
- `tests/test_automation_export.py`

Acceptance:

- `python scripts/export_automation.py --format json` succeeds.
- cron and Windows exports contain expected tasks.
- Automation tasks contain no real secrets.

### General Guardrails

- Do not commit `.env`, `config/user.yaml`, logs, runtime knowledge base data, `node_modules`, or build outputs.
- Do not hard-code API keys.
- Keep crawler and parser changes isolated by source.
- Prefer fixture tests over live network tests for CI-style verification.
- Run compile, tests, and frontend build before release.
