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

- Do not invoke an external model unless the user or runtime command explicitly enables summarization.
- Do not write secrets, keys, cookies, or private user data into prompts, logs, or stored analysis.
- Invalid model output must degrade to an `analysis.error` field instead of crashing the crawler.
- Existing articles should not be re-analyzed unless the run explicitly enables a forced analysis update.
