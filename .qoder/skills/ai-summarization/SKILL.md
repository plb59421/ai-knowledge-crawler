---
name: ai-summarization
description: |
  使用项目摘要模板将文章整理为结构化分析结果，覆盖核心观点、技术细节、关键结果、应用方向、风险级别和重要性评分。
when_to_use: |
  当需要为文章生成技术摘要、研究要点、实验结论、应用影响或人工复核材料时使用。
disable-model-invocation: false
user-invocable: true
allowed-tools: ["python"]
---

# Content Summarization

默认读取 `.qoder/prompts/summarize.st` 模板。

输出字段：

1. `core_points`
2. `technical_details`
3. `key_results`
4. `applications`
5. `risk_level`
6. `importance_score`

除非用户显式开启摘要并提供可用凭据，否则不得自动调用外部分析服务。
