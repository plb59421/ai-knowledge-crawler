# Project Modules

本文档定义项目的模块边界，后续修改时优先按模块定位，不跨层随意耦合。

## AI Capability Layer

位置：`.qoder/`

- `prompts/`: 模型提示词模板，当前主模板为 `summarize.st`。
- `skills/`: 项目级操作指南，用于指导信息源接入、解析器验证、AI 摘要和知识整理。
- `knowledge/`: 领域知识、信息源画像、可信度规则、主题分类体系。

约束：

- prompt 只定义输入输出和分析要求，不写业务存储逻辑。
- skill 只描述流程和检查标准，不包含真实密钥。
- knowledge 文档用于指导策略，不作为运行时唯一事实来源。

## Engineering Layer

位置：`src/`

- `core/`: 数据模型、异常、crawler registry。
- `crawlers/`: 每个信息源独立目录，包含 `crawler.py` 和 `parser.py`。
- `ai/`: OpenAI-compatible client、mock client、结构化摘要器。
- `processors/`: 清洗、文档处理、文章后处理。
- `ranking/`: 中文标签、分类型评分、时效过滤、报告 payload 构建。
- `storage/`: 文件知识库存储、去重、索引、更新和历史记录。
- `utils/`: 配置、日志、代理等基础工具。
- `web_api/`: FastAPI API，实时读取 `knowledge_base` 并返回前端数据。

约束：

- crawler 只负责抓取原始内容，parser 只负责转换为 `Article`。
- AI 分析只在爬虫任务中执行，Web API 不触发模型调用。
- `KnowledgeStore` 是写入知识库的唯一入口。
- Web API 复用 `ReportDataExporter.build_payload()`，不另写排序规则。

## Entry Points

位置：`scripts/`

- `run_crawler.py`: 手动单源/多源抓取。
- `run_daily.py`: 定时任务入口，按 domestic/proxy/all 分组执行。
- `generate_report.py`: 兼容导出静态 report JSON。
- `serve_api.py`: 本地 FastAPI 服务入口。
- `schedule_windows.ps1`: Windows Task Scheduler 创建脚本。
- `local_test.py`: 本地 fixture 流水线测试。

## Web Layer

位置：`web/report/`

- Vite + TypeScript 前端。
- 默认请求 `/api/report`。
- 静态 JSON fallback 仅用于离线预览。
- 页面只展示两个榜单：`技术资讯` 和 `学术论文`。

## Runtime Data

位置：`knowledge_base/`

- `by_source/`: 主存储。
- `by_time/`: 时间视图。
- `by_topic/`: 主题视图。
- `index/`: URL、去重、全文索引。
- `metadata/`: crawl history、daily report。
- `exports/`: 静态兼容导出和前端构建产物。

默认不提交运行时数据。需要分享样例时应放入 `tests/fixtures/`。
