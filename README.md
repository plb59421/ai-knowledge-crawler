# AI Knowledge Crawler

AI 前沿知识爬虫用于定时抓取 AI 技术信息源，调用 OpenAI-compatible 模型完成结构化整理，写入本地文件知识库，并通过 Web API + Vite 前端实时读取、排序和展示。

## Architecture

```text
scheduled crawler
  -> crawler / parser
  -> AI analysis
  -> tag + rank
  -> knowledge_base
  -> FastAPI /api/report
  -> Vite report UI
```

核心原则：

- 爬虫任务负责采集、AI 整理、标签、评分和入库。
- Web 访问不触发模型调用，只实时读取知识库并排序。
- `knowledge_base/by_source` 是主存储，导出文件仅作为兼容和离线 fallback。
- 默认使用千问 DashScope OpenAI-compatible 接口。

## Modules

```text
.qoder/                 AI 能力层：skills、prompts、knowledge
config/                 源配置、全局设置、日志配置
scripts/                CLI 入口、每日任务、本地 API 启动、调度脚本
src/ai/                 LLM client、mock client、结构化摘要器
src/core/               Article / CrawlResult 模型、注册中心、异常
src/crawlers/           各信息源 crawler + parser
src/processors/         HTML / 文档 / 文章后处理
src/ranking/            中文标签、分类型评分、时效过滤、报告数据构建
src/storage/            文件知识库存储、去重、索引、历史记录
src/utils/              配置、日志、代理工具
src/web_api/            FastAPI 实时读库 API
tests/                  单元测试、fixture、API 和前端源检查
web/report/             Vite + TypeScript 报告前端
knowledge_base/         运行时知识库，默认不提交生成数据
logs/                   运行日志，默认不提交
```

更多模块说明见 [docs/MODULES.md](docs/MODULES.md)。

## Setup

```powershell
python -m pip install -r requirements.txt
cd web/report
npm install
```

配置千问 API：

```powershell
$env:DASHSCOPE_API_KEY="your_dashscope_api_key"
$env:OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL="qwen-plus"
```

也可以把这些变量配置到用户环境变量中。不要把真实 key 写入仓库。

## Run

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

## Validation

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

上线检查见 [docs/OPERATIONS.md](docs/OPERATIONS.md)。
