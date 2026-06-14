# AI Project Assets

[中文](#中文) | [English](#english)

---

## 中文

`.ai/` 保存工具中立的 AI 项目资产，用于辅助项目维护、信息源接入、提示词管理、知识整理和自动化调度。

### 目录结构

- `prompts/`: 运行时分析使用的提示词模板。
- `skills/`: 项目工作流和质量检查说明。
- `knowledge/`: 领域策略、主题分类、来源画像和可信度规则。
- `automation.yaml`: 可被外部 AI 工具读取，或导出为调度命令的自动化任务清单。

### 规则

- 不存储 API Key、Token、Cookie 或私有凭据。
- 工具特定集成文件应由 `automation.yaml` 生成，不应成为主配置来源。
- 运行时密钥属于 `config/user.yaml`，该文件被 Git 忽略。

---

## English

`.ai/` stores tool-neutral AI project assets for project maintenance, source onboarding, prompt management, knowledge curation, and automation scheduling.

### Structure

- `prompts/`: Prompt templates used by runtime analysis.
- `skills/`: Project workflows and quality checks.
- `knowledge/`: Domain policies, topic taxonomy, source profiles, and trust rules.
- `automation.yaml`: Automation tasks that external AI tools can read or convert into scheduler commands.

### Rules

- Do not store API keys, tokens, cookies, or private credentials.
- Tool-specific integration files should be generated from `automation.yaml`, not treated as the canonical configuration.
- Runtime secrets belong in `config/user.yaml`, which is ignored by Git.
