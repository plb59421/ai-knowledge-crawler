# Documentation Style Guide

[中文](#中文) | [English](#english)

---

## 中文

本项目文档参考成熟开源爬虫项目的结构化写法：顶部语言入口、清晰一句话定位、快速链接、核心特性、快速开始、进阶文档和验证命令。

### 基本结构

每个 Markdown 文档应包含：

1. 标题。
2. 语言入口：`[中文](#中文) | [English](#english)`。
3. 中文正文。
4. 英文正文。
5. 可复制的命令示例。

### 写作原则

- 中文和英文信息应等价，不要只翻译标题。
- 先给最短可运行路径，再给详细解释。
- 命令示例使用 fenced code block，并标注 shell 类型。
- 文件路径、命令、配置键使用反引号。
- 不在文档中写真实 API Key、Cookie、Token 或私有地址。
- 对 AI 工具可读的文档，应明确“修改点”和“验收标准”。

### README 结构

README 应包含：

- 项目一句话定位。
- 语言入口。
- 快速链接。
- 核心特性。
- 架构图或流程图。
- 安装和配置。
- 快速运行。
- 自动化导出。
- 验证命令。

### 目录说明

- 面向用户的文档放在 `README.md` 和 `docs/`。
- 面向 AI 工具的项目资产放在 `.ai/`。
- 运行时数据说明放在 `knowledge_base/README.md`。
- 长期规则和来源规范放在 `.ai/knowledge/`。

---

## English

Project documentation follows the structure used by mature open-source crawler projects: language selector, concise positioning, quick links, key features, getting started, advanced docs, and validation commands.

### Basic Structure

Every Markdown document should include:

1. Title.
2. Language selector: `[中文](#中文) | [English](#english)`.
3. Chinese section.
4. English section.
5. Copyable command examples.

### Writing Rules

- Chinese and English content should be equivalent, not just translated headings.
- Put the shortest runnable path before detailed explanations.
- Use fenced code blocks with shell types for commands.
- Use backticks for file paths, commands, and configuration keys.
- Do not write real API keys, cookies, tokens, or private addresses in docs.
- AI-readable docs should clearly state touch points and acceptance criteria.

### README Structure

README should include:

- One-sentence project positioning.
- Language selector.
- Quick links.
- Key features.
- Architecture or flow diagram.
- Installation and configuration.
- Quick start.
- Automation export.
- Validation commands.

### Directory Guidance

- User-facing docs live in `README.md` and `docs/`.
- AI tool-facing project assets live in `.ai/`.
- Runtime data guidance lives in `knowledge_base/README.md`.
- Long-lived rules and source policies live in `.ai/knowledge/`.
