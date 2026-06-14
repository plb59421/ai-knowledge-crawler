---
name: parser-validation
description: |
  校验信息源解析器能否从离线样本中稳定提取文章字段，并在字段缺失、结构变化或空内容时安全降级。
when_to_use: |
  当新增或修改 parser、CSS selector、接口字段映射、fixture 或解析测试时使用。
disable-model-invocation: true
user-invocable: true
allowed-tools: ["python"]
---

# Parser Validation

Parser 必须保证：

1. 不因标题、日期、作者或正文缺失而崩溃。
2. 至少返回一个 `Article`，或清晰返回空列表。
3. `source`、`title`、`url` 应尽量非空。
4. 正文解析失败时保留标题和 URL，方便后续排查。
5. 每个 parser 至少有一个离线 fixture 测试。
6. 接口源应覆盖空数组、缺失字段和异常字段类型。
