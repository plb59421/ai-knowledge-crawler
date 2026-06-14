# Project Modules

[中文](#中文) | [English](#english)

---

## 中文

本文件定义项目模块边界。后续由 AI 工具或人工维护时，应优先按模块定位，不跨层混合修改。

### AI 能力层

位置：`.ai/`

- `prompts/`: 运行时提示词模板，当前主模板是 `summarize.st`。
- `skills/`: 项目级工作流说明，覆盖信息源接入、解析器验证、内容摘要、知识整理。
- `knowledge/`: 主题分类、来源可信度、来源画像和安全规范。
- `automation.yaml`: 定时采集和本地服务的标准自动化任务定义。
- `PROJECT.md`: `.ai/` 目录的工具中立规则。

约束：

- 不存储 API Key、Cookie、Token 或私有凭据。
- 工具特定文件应由 `automation.yaml` 导出生成，不直接作为主配置。
- 运行时私密配置放在 `config/user.yaml`。

### 工程能力层

位置：`src/`

- `core/`: `Article`、`CrawlResult`、注册中心和共享异常。
- `crawlers/`: 每个信息源一个独立目录，包含 crawler 和 parser。
- `ai/`: OpenAI-compatible client、mock client 和结构化摘要器。
- `processors/`: HTML、文档和文章后处理。
- `ranking/`: 中文标签、分类型评分、时效过滤和报告数据构建。
- `storage/`: 文件知识库写入、去重、索引、更新和历史记录。
- `utils/`: 配置、日志和代理工具。
- `web_api/`: 实时读取 `knowledge_base` 的 FastAPI 服务。

约束：

- crawler 只负责抓取原始内容；parser 只负责转换为 `Article`。
- AI 分析只在爬虫任务中执行，Web 访问不触发模型调用。
- `KnowledgeStore` 是文章入库的统一入口。
- Web API 应复用现有报告查询和排序逻辑。

### 入口脚本

位置：`scripts/`

- `run_crawler.py`: 手动单源或多源爬取。
- `run_daily.py`: 按 `domestic`、`proxy`、`all` 分组执行定时任务。
- `serve_api.py`: 本地 FastAPI 服务入口。
- `generate_report.py`: 兼容用静态报告数据导出。
- `export_automation.py`: 将 `.ai/automation.yaml` 导出为 JSON、Markdown、cron 或 Windows 调度命令。
- `schedule_windows.ps1`: 旧版 Windows Task Scheduler 辅助脚本。
- `local_test.py`: 本地 fixture 流水线。

### Web 层

位置：`web/report/`

- Vite + TypeScript 报告前端。
- 默认请求 `/api/report`。
- 静态 JSON 仅作为离线 fallback。
- 页面只展示两个榜单：`技术资讯` 和 `学术论文`。

### 桌面应用层

位置：`desktop_app/`

- EXE 桌面应用的隔离工作区。
- 用于存放未来 Tauri 桌面壳、Python sidecar、安装资源和发布文档。
- 不迁移或复制主项目的 `src/`、`scripts/`、`web/report/`。
- 不提交真实用户配置、知识库、日志或安装产物。

### 运行时数据

位置：`knowledge_base/`

- `by_source/`: 文章主存储。
- `by_time/`: 时间视图。
- `by_topic/`: 主题视图。
- `index/`: URL、去重和搜索索引。
- `metadata/`: 抓取历史和日报。
- `exports/`: 兼容导出和前端构建产物。

运行时数据默认不提交。稳定样例应放入 `tests/fixtures/`。

---

## English

This document defines module boundaries. Future AI-assisted or human changes should start from the owning module and avoid mixing responsibilities across layers.

### AI Capability Layer

Location: `.ai/`

- `prompts/`: Runtime prompt templates. Current main template: `summarize.st`.
- `skills/`: Project workflow instructions for source onboarding, parser validation, content summarization, and knowledge curation.
- `knowledge/`: Topic taxonomy, source trust policy, source profiles, and safety rules.
- `automation.yaml`: Canonical automation tasks for scheduled ingestion and local services.
- `PROJECT.md`: Tool-neutral rules for the `.ai/` directory.

Constraints:

- Store no API keys, cookies, tokens, or private credentials.
- Tool-specific files should be generated from `automation.yaml` instead of becoming the canonical config.
- Runtime secrets belong in `config/user.yaml`.

### Engineering Layer

Location: `src/`

- `core/`: `Article`, `CrawlResult`, registry, and shared exceptions.
- `crawlers/`: One directory per source, with crawler and parser implementations.
- `ai/`: OpenAI-compatible client, mock client, and structured summarizer.
- `processors/`: HTML, document, and article post-processing.
- `ranking/`: Chinese tags, profile-specific scoring, freshness filtering, and report payload construction.
- `storage/`: File knowledge base writes, deduplication, indexes, updates, and history.
- `utils/`: Configuration, logging, and proxy helpers.
- `web_api/`: FastAPI service that reads `knowledge_base` in real time.

Constraints:

- Crawlers fetch raw content; parsers convert raw content into `Article`.
- AI analysis runs in crawler jobs only, not during Web access.
- `KnowledgeStore` is the unified article storage entry point.
- Web API should reuse the existing report query and ranking logic.

### Entry Scripts

Location: `scripts/`

- `run_crawler.py`: Manual single-source or multi-source crawler.
- `run_daily.py`: Scheduled grouped crawler for `domestic`, `proxy`, or `all`.
- `serve_api.py`: Local FastAPI service.
- `generate_report.py`: Compatibility static report data export.
- `export_automation.py`: Exports `.ai/automation.yaml` to JSON, Markdown, cron, or Windows scheduler commands.
- `schedule_windows.ps1`: Legacy Windows Task Scheduler helper.
- `local_test.py`: Local fixture pipeline.

### Web Layer

Location: `web/report/`

- Vite + TypeScript report UI.
- Requests `/api/report` by default.
- Static JSON is only an offline fallback.
- The UI shows two lists: `技术资讯` and `学术论文`.

### Desktop App Layer

Location: `desktop_app/`

- Isolated workspace for the EXE desktop application.
- Stores future Tauri shell files, Python sidecar files, installer resources, and release docs.
- Does not move or duplicate root-level `src/`, `scripts/`, or `web/report/`.
- Does not commit real user config, knowledge base data, logs, or installer artifacts.

### Runtime Data

Location: `knowledge_base/`

- `by_source/`: Primary article storage.
- `by_time/`: Time view.
- `by_topic/`: Topic view.
- `index/`: URL, deduplication, and search indexes.
- `metadata/`: Crawl history and daily reports.
- `exports/`: Compatibility exports and frontend build output.

Runtime data is ignored by Git. Stable examples should live in `tests/fixtures/`.
