---
name: source-onboarding
description: |
  Guide the onboarding of a new information source, covering configuration,
  crawler, parser, fixture, tests, registry wiring, runtime validation, and rollback.
when_to_use: |
  Use when adding a new webpage source, API source, paper source, news source,
  or community source.
disable-model-invocation: true
user-invocable: true
allowed-tools: ["python"]
---

# Source Onboarding

[中文](#中文) | [English](#english)

---

## 中文

新增信息源必须完成：

1. 在 `config/sources.yaml` 增加 source 配置。
2. 在 `src/crawlers/<source>/` 增加 `crawler.py`、`parser.py` 和 `__init__.py`。
3. 在 `src/crawlers/registry_config.py` 注册 crawler 和 parser。
4. 在 `tests/fixtures/` 增加最小 HTML、XML 或 JSON fixture。
5. 在 parser 测试中验证 `title`、`url`、`source`、`full_text` 等关键字段。
6. 标明是否需要代理、是否需要动态页面渲染、是否有访问限制。
7. 不稳定来源先保留手动运行入口，不加入默认每日分组。

验收命令：

```powershell
python -m compileall -q src scripts
pytest
python scripts/run_crawler.py --source <source> --max-pages 1
```

---

## English

A new source must include:

1. Source configuration in `config/sources.yaml`.
2. `crawler.py`, `parser.py`, and `__init__.py` under `src/crawlers/<source>/`.
3. Registry wiring in `src/crawlers/registry_config.py`.
4. A minimal HTML, XML, or JSON fixture in `tests/fixtures/`.
5. Parser tests for key fields such as `title`, `url`, `source`, and `full_text`.
6. Clear notes on proxy needs, dynamic rendering needs, and access limits.
7. Manual-only status for unstable sources until they are validated.

Acceptance commands:

```powershell
python -m compileall -q src scripts
pytest
python scripts/run_crawler.py --source <source> --max-pages 1
```
