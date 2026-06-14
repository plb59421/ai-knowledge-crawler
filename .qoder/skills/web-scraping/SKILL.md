---
name: web-scraping
description: |
  指导项目执行网页与接口数据抓取，覆盖抓取器选型、代理配置、请求限速、列表页发现、详情页提取和失败降级。
when_to_use: |
  当需要新增、修复或验证信息源抓取流程时使用，尤其适用于静态页面、动态页面、接口源和需要代理访问的站点。
disable-model-invocation: true
user-invocable: true
allowed-tools: ["python"]
---

# Web Scraping

## 抓取器选型

1. 静态 HTML 页面优先使用轻量抓取器。
2. 依赖浏览器渲染的页面使用动态抓取器。
3. JSON、Atom、RSS 等接口源优先使用结构化请求库。
4. 需要规避简单反爬的页面可切换到更接近真实浏览器行为的抓取器。

## 实现规范

1. 配置优先从 `config/sources.yaml` 读取，不在代码中重复写死。
2. 每个源必须包含 crawler、parser、注册项和最小 fixture 测试。
3. parser 必须容忍标题、日期、作者、正文缺失，并返回可诊断的结果。
4. 抓取失败时记录结构化错误，不吞掉异常上下文。
5. 列表页只负责发现链接，详情页负责提取正文和元数据。

## 代理与限速

1. 代理优先从 `HTTP_PROXY`、`HTTPS_PROXY` 读取。
2. 不需要代理的源应清理代理环境，避免误走本地代理。
3. 默认保留请求间隔，遇到 429 或连接异常时退避重试。
4. 对第三方接口源优先降低频率和单次请求量。

## 验收

1. `python -m compileall -q src scripts`
2. `pytest`
3. 单源试跑至少返回可解释的统计结果。
