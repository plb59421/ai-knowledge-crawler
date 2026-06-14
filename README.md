# AI Knowledge Crawler

[中文](#中文) | [English](#english)

Tool-neutral AI knowledge crawler for scheduled collection, AI-assisted analysis, local knowledge storage, and real-time Web reporting.

---

## 中文

AI Knowledge Crawler 是一个面向 AI 前沿技术动态的本地知识采集项目。它定时从技术博客、研究机构、论文 API、新闻聚合站等来源抓取内容，经过 AI 整理、中文标签、分类评分和时效过滤后写入本地知识库，再由 Web API 实时读取并展示。

### 快速链接

- [模块说明](docs/MODULES.md)
- [运维指南](docs/OPERATIONS.md)
- [AI 修改指南](docs/AI_CHANGE_GUIDE.md)
- [文档规范](docs/DOCUMENTATION_STYLE.md)
- [自动化清单](.ai/automation.yaml)
- [前端报告](web/report/)

### 核心特性

- 多源爬虫：支持博客、媒体、论文 API、研究机构和动态页面。
- AI 整理入库：爬取后可调用 OpenAI-compatible 模型生成结构化分析。
- 中文标签体系：行业、AI 技术、文章类型三类标签。
- 分类型评分：学术论文和技术资讯使用独立评分体系。
- 实时读库 Web：访问页面时由本地 API 实时读取 `knowledge_base`。
- 工具中立自动化：`.ai/automation.yaml` 可导出为 JSON、Markdown、cron 或 Windows 调度命令。

### 架构

```text
scheduled crawler
  -> crawler / parser
  -> AI analysis
  -> tag + rank
  -> knowledge_base
  -> FastAPI /api/report
  -> Vite report UI
```

### 安装

```powershell
python -m pip install -r requirements.txt
cd web/report
npm install
```

复制本地配置模板：

```powershell
Copy-Item config/user.example.yaml config/user.yaml
```

编辑 `config/user.yaml`，填写本地私有配置：

```yaml
llm:
  api_key: "your_dashscope_api_key"
  model: qwen-plus
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
```

`config/user.yaml` 已被 Git 忽略。不要把真实 API Key 写入仓库文件。

### 快速运行

列出信息源：

```powershell
python scripts/run_crawler.py --list
```

单源抓取并调用 AI 整理：

```powershell
python scripts/run_crawler.py --source qbitai --max-pages 1 --no-proxy --summarize --analysis-limit 1
```

每日任务：

```powershell
python scripts/run_daily.py --group all --max-pages 5 --summarize --analysis-limit 10
```

启动本地 API：

```powershell
python scripts/serve_api.py --host 127.0.0.1 --port 8000
```

启动前端：

```powershell
cd web/report
npm run dev
```

访问：

```text
http://127.0.0.1:5173
```

### 自动化导出

```powershell
python scripts/export_automation.py --format json
python scripts/export_automation.py --format markdown
python scripts/export_automation.py --format windows
python scripts/export_automation.py --format cron
```

### 验证

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

---

## English

AI Knowledge Crawler is a local knowledge ingestion project for frontier AI updates. It periodically collects content from technical blogs, research labs, paper APIs, and news aggregators, then stores AI-analyzed, tagged, ranked, and freshness-filtered articles in a local knowledge base. The Web UI reads from the local API in real time.

### Quick Links

- [Modules](docs/MODULES.md)
- [Operations](docs/OPERATIONS.md)
- [AI Change Guide](docs/AI_CHANGE_GUIDE.md)
- [Documentation Style](docs/DOCUMENTATION_STYLE.md)
- [Automation Manifest](.ai/automation.yaml)
- [Report UI](web/report/)

### Key Features

- Multi-source crawler for blogs, media sites, paper APIs, research labs, and dynamic pages.
- AI-assisted ingestion with an OpenAI-compatible model after crawling.
- Chinese tag system for industries, AI technologies, and content types.
- Separate ranking profiles for academic papers and general technical content.
- Real-time local Web API that reads from `knowledge_base`.
- Tool-neutral automation via `.ai/automation.yaml`, exportable to JSON, Markdown, cron, or Windows scheduler commands.

### Architecture

```text
scheduled crawler
  -> crawler / parser
  -> AI analysis
  -> tag + rank
  -> knowledge_base
  -> FastAPI /api/report
  -> Vite report UI
```

### Installation

```powershell
python -m pip install -r requirements.txt
cd web/report
npm install
```

Copy the local configuration template:

```powershell
Copy-Item config/user.example.yaml config/user.yaml
```

Edit `config/user.yaml` with local-only values:

```yaml
llm:
  api_key: "your_dashscope_api_key"
  model: qwen-plus
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
```

`config/user.yaml` is ignored by Git. Never commit real API keys.

### Quick Start

List sources:

```powershell
python scripts/run_crawler.py --list
```

Crawl one source with AI analysis:

```powershell
python scripts/run_crawler.py --source qbitai --max-pages 1 --no-proxy --summarize --analysis-limit 1
```

Run daily groups:

```powershell
python scripts/run_daily.py --group all --max-pages 5 --summarize --analysis-limit 10
```

Start the local API:

```powershell
python scripts/serve_api.py --host 127.0.0.1 --port 8000
```

Start the frontend:

```powershell
cd web/report
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

### Automation Export

```powershell
python scripts/export_automation.py --format json
python scripts/export_automation.py --format markdown
python scripts/export_automation.py --format windows
python scripts/export_automation.py --format cron
```

### Validation

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```
