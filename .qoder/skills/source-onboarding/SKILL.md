---
name: source-onboarding
description: |
  为项目新增信息源时使用，覆盖配置、crawler、parser、fixture、测试、注册、运行验证和失败回退。
when_to_use: |
  当需要接入新的网页源、接口源、论文源、新闻源或社区源时使用。
disable-model-invocation: true
user-invocable: true
allowed-tools: ["python"]
---

# Source Onboarding

新增信息源必须完成：

1. 在 `config/sources.yaml` 增加 source 配置。
2. 在 `src/crawlers/{source}/` 增加 crawler、parser、`__init__.py`。
3. 在 `src/crawlers/registry_config.py` 注册。
4. 在 `tests/fixtures/` 增加最小 HTML、XML 或 JSON fixture。
5. 在 parser 测试中验证 `title`、`url`、`source`、`full_text`。
6. 标明是否需要代理、是否需要动态页面渲染、是否有访问限制。
7. 对不可稳定访问的源保留手动运行入口，不加入默认日常分组。
