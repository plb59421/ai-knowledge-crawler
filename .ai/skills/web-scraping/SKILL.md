---
name: web-scraping
description: |
  Guide webpage and API data extraction for this project, including fetcher
  selection, proxy configuration, rate limits, list-page discovery, detail-page
  extraction, and graceful fallback.
when_to_use: |
  Use when adding, fixing, or validating source crawling flows for static pages,
  dynamic pages, API sources, or proxy-required sources.
disable-model-invocation: true
user-invocable: true
allowed-tools: ["python"]
---

# Web Scraping

[中文](#中文) | [English](#english)

---

## 中文

### 抓取器选型

1. 静态 HTML 页面优先使用轻量 HTTP 抓取器。
2. 依赖浏览器渲染的页面使用动态抓取器。
3. JSON、Atom、RSS 等接口源优先使用结构化请求。
4. 需要规避简单反爬的页面，可切换到更接近真实浏览器行为的抓取器。

### 实现规范

1. 配置优先从 `config/sources.yaml` 读取，不在代码中重复写死。
2. 每个源必须包含 crawler、parser、注册项和最小 fixture 测试。
3. parser 必须容忍标题、日期、作者、正文缺失，并返回可诊断结果。
4. 抓取失败时记录结构化错误，不吞掉异常上下文。
5. 列表页只负责发现链接，详情页负责正文和元数据提取。

### 代理与限速

1. 代理配置优先从 `config/user.yaml` 读取，可兼容环境变量。
2. 不需要代理的源应明确使用 `--no-proxy` 或配置为无需代理。
3. 遇到 429 或连接异常时应降速并重试。
4. 第三方 API 源应降低频率和单次请求量。

### 验收

```powershell
python -m compileall -q src scripts
pytest
python scripts/run_crawler.py --source <source> --max-pages 1
```

---

## English

### Fetcher Selection

1. Prefer lightweight HTTP fetchers for static HTML pages.
2. Use dynamic fetchers for browser-rendered pages.
3. Prefer structured requests for JSON, Atom, RSS, or API sources.
4. Switch to a browser-like fetcher when simple anti-bot behavior must be handled.

### Implementation Rules

1. Read source settings from `config/sources.yaml`; avoid hard-coded duplicates.
2. Every source must include crawler, parser, registry wiring, and a minimal fixture test.
3. Parsers must tolerate missing title, date, author, and body fields.
4. Crawl failures should log structured errors without losing exception context.
5. List pages discover links; detail pages extract content and metadata.

### Proxy and Rate Limits

1. Prefer proxy settings from `config/user.yaml`, with environment variables as compatibility fallback.
2. Sources that do not need a proxy should explicitly use `--no-proxy` or source config.
3. Slow down and retry on 429 or connection failures.
4. Third-party APIs should use conservative request frequency and page sizes.

### Acceptance

```powershell
python -m compileall -q src scripts
pytest
python scripts/run_crawler.py --source <source> --max-pages 1
```
