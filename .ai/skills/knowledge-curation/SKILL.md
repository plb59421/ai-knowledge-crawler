---
name: knowledge-curation
description: |
  将抓取文章整理为多视图知识库，覆盖来源归档、时间归档、主题归档、索引、去重和人工阅读版导出。
when_to_use: |
  当需要整理、去重、索引、导出、迁移或复核知识库内容时使用。
disable-model-invocation: true
user-invocable: true
allowed-tools: ["python"]
---

# Knowledge Curation

知识库整理规则：

1. URL 是第一去重键。
2. `source + title` 是第二去重键。
3. `by_source` 是主存储路径。
4. `by_time` 和 `by_topic` 是派生视图。
5. `index/url_index.json` 用于 URL 查重和定位。
6. `metadata/dedup_records.json` 用于标题级去重。
7. Markdown 导出用于人工阅读，不作为主数据源。
8. 旧索引结构不符合预期时应记录错误并安全重建。
