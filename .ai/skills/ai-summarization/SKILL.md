---
name: ai-summarization
description: |
  Generate structured article analysis with core points, technical details,
  key results, application directions, risk level, and importance score.
when_to_use: |
  Use when a crawled article needs structured analysis before being stored in
  the knowledge base.
disable-model-invocation: false
user-invocable: true
allowed-tools: ["python"]
---

# Content Summarization

[中文](#中文) | [English](#english)

---

## 中文

默认提示词模板：

```text
.ai/prompts/summarize.st
```

期望输出字段：

1. `core_points`
2. `technical_details`
3. `key_results`
4. `applications`
5. `risk_level`
6. `importance_score`

规则：

- 只有当用户或运行命令显式启用摘要时，才能调用外部模型。
- 不要把密钥、Cookie、Token 或用户私有数据写入 prompt、日志或分析结果。
- 非法模型输出应降级写入 `analysis.error`，不能导致爬虫崩溃。
- 已存在文章默认不重新分析，除非运行命令显式开启强制分析。

---

## English

Default prompt template:

```text
.ai/prompts/summarize.st
```

Expected output fields:

1. `core_points`
2. `technical_details`
3. `key_results`
4. `applications`
5. `risk_level`
6. `importance_score`

Rules:

- Invoke an external model only when the user or runtime command explicitly enables summarization.
- Do not write secrets, cookies, tokens, or private user data into prompts, logs, or stored analysis.
- Invalid model output must degrade to an `analysis.error` field instead of crashing the crawler.
- Existing articles should not be re-analyzed unless the run explicitly enables forced analysis.
