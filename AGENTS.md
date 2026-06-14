# AI Knowledge Crawler Agent Guide

[中文](#中文) | [English](#english)

---

## 中文

### 项目定位

本项目用于定时抓取 AI 前沿内容，完成 AI 整理、中文标签、评分排序、知识库存储，并通过本地 Web API 实时展示。

### 两层架构

- AI 能力层：`.ai/`
  - `prompts/`: 提示词模板
  - `skills/`: 项目级工作流说明
  - `knowledge/`: 来源画像、主题分类、可信度和安全规范
  - `automation.yaml`: 工具中立的自动化任务清单
- 工程能力层：`src/`
  - 爬虫、解析、AI 分析、后处理、评分、存储、Web API

### 关键路径

```text
.ai/                         AI 项目资产
config/user.example.yaml      本地配置模板
config/user.yaml              本地私有配置，禁止提交
config/sources.yaml           信息源配置
scripts/run_crawler.py        手动爬取入口
scripts/run_daily.py          定时任务入口
scripts/serve_api.py          本地 API 入口
scripts/export_automation.py  自动化清单导出
web/report/                   Vite 报告前端
knowledge_base/               运行时知识库，默认不提交
```

### 运行链路

```text
定时爬虫
  -> crawler / parser
  -> AI analysis
  -> tag + rank
  -> KnowledgeStore
  -> FastAPI /api/report
  -> Web UI
```

Web 访问只能读取 `knowledge_base`，不得触发模型调用。

### 本地配置

```powershell
Copy-Item config/user.example.yaml config/user.yaml
```

不要提交 API Key、Cookie、Token、日志、运行时知识库、`node_modules` 或构建产物。

### 自动化入口

```powershell
python scripts/export_automation.py --format json
python scripts/export_automation.py --format markdown
python scripts/export_automation.py --format cron
python scripts/export_automation.py --format windows
```

### 验证命令

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

### 修改边界

- 新信息源改动应集中在 `config/sources.yaml`、`src/crawlers/<source>/`、注册文件和 fixture 测试。
- AI 分析改动应集中在 `.ai/prompts/`、`src/ai/`、`src/core/models.py` 和相关测试。
- 标签与评分改动应集中在 `src/ranking/`。
- Web 展示不得调用 LLM，只能通过 API 读取知识库。

---

## English

### Project Purpose

This project periodically collects frontier AI content, runs AI-assisted analysis, applies Chinese tags, ranks articles, stores them in a local knowledge base, and serves them through a local Web API.

### Two-Layer Architecture

- AI capability layer: `.ai/`
  - `prompts/`: Prompt templates
  - `skills/`: Project workflow instructions
  - `knowledge/`: Source profiles, topic taxonomy, trust rules, and safety rules
  - `automation.yaml`: Tool-neutral automation manifest
- Engineering layer: `src/`
  - Crawlers, parsers, AI analysis, post-processing, ranking, storage, and Web API

### Important Paths

```text
.ai/                         AI project assets
config/user.example.yaml      Local configuration template
config/user.yaml              Local private config, never commit
config/sources.yaml           Source configuration
scripts/run_crawler.py        Manual crawler entry point
scripts/run_daily.py          Scheduled crawler entry point
scripts/serve_api.py          Local API entry point
scripts/export_automation.py  Automation manifest exporter
web/report/                   Vite report UI
knowledge_base/               Runtime knowledge base, ignored by Git
```

### Runtime Flow

```text
scheduled crawler
  -> crawler / parser
  -> AI analysis
  -> tag + rank
  -> KnowledgeStore
  -> FastAPI /api/report
  -> Web UI
```

Web access must only read from `knowledge_base`; it must not invoke an LLM.

### Local Configuration

```powershell
Copy-Item config/user.example.yaml config/user.yaml
```

Never commit API keys, cookies, tokens, logs, runtime knowledge base data, `node_modules`, or build artifacts.

### Automation Entry Point

```powershell
python scripts/export_automation.py --format json
python scripts/export_automation.py --format markdown
python scripts/export_automation.py --format cron
python scripts/export_automation.py --format windows
```

### Validation Commands

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

### Change Boundaries

- New source changes should stay around `config/sources.yaml`, `src/crawlers/<source>/`, registry wiring, and fixture tests.
- AI analysis changes should stay around `.ai/prompts/`, `src/ai/`, `src/core/models.py`, and related tests.
- Tagging and ranking changes should stay in `src/ranking/`.
- The Web UI must not call an LLM; it should read the knowledge base through the API.
