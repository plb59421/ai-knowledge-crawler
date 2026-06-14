# Operations Guide

[中文](#中文) | [English](#english)

---

## 中文

### 环境准备

安装 Python 依赖：

```powershell
python -m pip install -r requirements.txt
```

安装前端依赖：

```powershell
cd web/report
npm install
```

复制本地配置：

```powershell
Copy-Item config/user.example.yaml config/user.yaml
```

填写 `config/user.yaml`：

```yaml
llm:
  api_key: "your_dashscope_api_key"
  model: qwen-plus
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1

proxy:
  enabled: true
  url: ""

runtime:
  default_analysis_limit: 10
  api_host: 127.0.0.1
  api_port: 8000
```

`config/user.yaml` 已被 Git 忽略。不要提交真实 API Key。

### 每日任务

国内和 API 源：

```powershell
python scripts/run_daily.py --group domestic --max-pages 5 --summarize --analysis-limit 10
```

需要代理的源：

```powershell
python scripts/run_daily.py --group proxy --max-pages 3 --summarize --analysis-limit 10
```

全部默认源：

```powershell
python scripts/run_daily.py --group all --max-pages 5 --summarize --analysis-limit 10
```

说明：

- `--summarize` 开启真实模型调用。
- `--analysis-limit` 限制单次运行的 AI 分析数量。
- 已存在文章默认跳过 AI 分析。
- `--force-analyze` 可用于重新分析并更新已有文章。

### 自动化清单

标准自动化定义位于 `.ai/automation.yaml`。

导出给外部 AI 工具或调度系统：

```powershell
python scripts/export_automation.py --format json
python scripts/export_automation.py --format markdown
python scripts/export_automation.py --format cron
python scripts/export_automation.py --format windows
```

调度定义应优先修改 `.ai/automation.yaml`，再重新导出。

### Web 运行

启动 API：

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

API 示例：

```text
GET http://127.0.0.1:8000/api/health
GET http://127.0.0.1:8000/api/report
GET http://127.0.0.1:8000/api/report?profile=academic&limit=50
GET http://127.0.0.1:8000/api/report?tag=LLM&pass_score=0
```

### 发布检查

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

额外检查：

- `git status --short` 不应包含运行时数据。
- 密钥扫描不应命中真实 Key。
- `python scripts/run_crawler.py --list` 应列出已注册信息源。

### 已知运行事项

- 部分国际源需要本地代理。
- Scrapling 的代理配置警告不影响当前运行。
- ArXiv PDF 提取失败时会降级使用 API metadata 和 summary。
- `report_latest.json` 仅为兼容导出，不是 Web 主数据路径。

---

## English

### Environment

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install frontend dependencies:

```powershell
cd web/report
npm install
```

Copy local configuration:

```powershell
Copy-Item config/user.example.yaml config/user.yaml
```

Fill `config/user.yaml`:

```yaml
llm:
  api_key: "your_dashscope_api_key"
  model: qwen-plus
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1

proxy:
  enabled: true
  url: ""

runtime:
  default_analysis_limit: 10
  api_host: 127.0.0.1
  api_port: 8000
```

`config/user.yaml` is ignored by Git. Never commit real API keys.

### Daily Jobs

Domestic and API sources:

```powershell
python scripts/run_daily.py --group domestic --max-pages 5 --summarize --analysis-limit 10
```

Proxy-required sources:

```powershell
python scripts/run_daily.py --group proxy --max-pages 3 --summarize --analysis-limit 10
```

All default sources:

```powershell
python scripts/run_daily.py --group all --max-pages 5 --summarize --analysis-limit 10
```

Notes:

- `--summarize` enables real model calls.
- `--analysis-limit` caps AI analyses per run.
- Existing articles skip AI analysis by default.
- `--force-analyze` re-analyzes and updates existing articles.

### Automation Manifest

The canonical automation definition is `.ai/automation.yaml`.

Export it for external AI tools or schedulers:

```powershell
python scripts/export_automation.py --format json
python scripts/export_automation.py --format markdown
python scripts/export_automation.py --format cron
python scripts/export_automation.py --format windows
```

Edit `.ai/automation.yaml` first when schedule definitions change, then export again.

### Web Runtime

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

### Release Checklist

```powershell
python -m compileall -q src scripts
pytest
cd web/report
npm.cmd run build
```

Additional checks:

- `git status --short` should not include runtime data.
- Secret scan should not find real keys.
- `python scripts/run_crawler.py --list` should list registered sources.

### Known Runtime Notes

- Some international sources require a local proxy.
- Scrapling proxy configuration warnings do not block current runs.
- ArXiv PDF extraction may fall back to API metadata and summary.
- `report_latest.json` is a compatibility export, not the primary Web data path.
