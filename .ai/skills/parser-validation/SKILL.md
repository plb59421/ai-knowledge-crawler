---
name: parser-validation
description: |
  Validate that source parsers can extract stable article fields from offline
  fixtures and degrade safely when fields are missing or structures change.
when_to_use: |
  Use when adding or changing parsers, CSS selectors, API field mappings,
  fixtures, or parser tests.
disable-model-invocation: true
user-invocable: true
allowed-tools: ["python"]
---

# Parser Validation

[中文](#中文) | [English](#english)

---

## 中文

parser 必须保证：

1. 不因标题、日期、作者或正文缺失而崩溃。
2. 至少返回一个 `Article`，或清晰返回空列表。
3. `source`、`title`、`url` 应尽量非空。
4. 正文解析失败时保留标题和 URL，便于后续排查。
5. 每个 parser 至少有一个离线 fixture 测试。
6. API 源应覆盖空数组、缺失字段和异常字段类型。

推荐测试：

```powershell
pytest tests/test_parsers.py
python -m compileall -q src scripts
```

---

## English

Parsers must guarantee:

1. Missing title, date, author, or body fields do not crash parsing.
2. They return at least one `Article`, or clearly return an empty list.
3. `source`, `title`, and `url` should be non-empty whenever possible.
4. If body extraction fails, keep title and URL for debugging.
5. Every parser should have at least one offline fixture test.
6. API sources should cover empty arrays, missing fields, and unexpected field types.

Recommended tests:

```powershell
pytest tests/test_parsers.py
python -m compileall -q src scripts
```
