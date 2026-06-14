---
name: knowledge-curation
description: |
  Organize crawled articles into a multi-view file knowledge base with source
  archives, time views, topic views, indexes, deduplication, and readable exports.
when_to_use: |
  Use when organizing, deduplicating, indexing, exporting, migrating, or reviewing
  knowledge base content.
disable-model-invocation: true
user-invocable: true
allowed-tools: ["python"]
---

# Knowledge Curation

[中文](#中文) | [English](#english)

---

## 中文

知识库整理规则：

1. URL 是第一去重键。
2. `source + title` 是第二去重键。
3. `by_source` 是主存储路径。
4. `by_time` 和 `by_topic` 是派生视图。
5. `index/url_index.json` 用于 URL 查重和定位。
6. `metadata/dedup_records.json` 用于标题级去重。
7. Markdown 或 HTML 导出用于人工阅读，不作为主数据源。
8. 索引结构异常时应记录错误并安全重建。

验证重点：

```powershell
pytest tests/test_models_storage_registry.py
pytest tests/test_report_data.py
```

---

## English

Knowledge base curation rules:

1. URL is the primary deduplication key.
2. `source + title` is the secondary deduplication key.
3. `by_source` is the canonical storage path.
4. `by_time` and `by_topic` are derived views.
5. `index/url_index.json` is used for URL lookup and deduplication.
6. `metadata/dedup_records.json` is used for title-level deduplication.
7. Markdown or HTML exports are for human reading, not canonical storage.
8. Unexpected index structures should be logged and safely rebuilt.

Validation focus:

```powershell
pytest tests/test_models_storage_registry.py
pytest tests/test_report_data.py
```
