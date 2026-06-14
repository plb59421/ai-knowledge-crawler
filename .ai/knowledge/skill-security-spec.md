# Skill Security Specification

[中文](#中文) | [English](#english)

---

## 中文

本规范用于检查 `.ai/skills/` 下的项目级工作流说明，目标是降低提示注入、敏感信息泄露、权限过大和供应链风险。

### 风险类别

1. 提示注入：外部内容试图覆盖项目指令。
2. 敏感信息泄露：API Key、Cookie、Token、用户数据被写入日志或文档。
3. 权限过大：skill 声明了不必要的工具或危险操作。
4. 供应链风险：未经审查的脚本、依赖或外部服务被引入。
5. 数据污染：不可信内容直接进入知识库或提示词。

### 必须规则

| 编号 | 规则 |
| --- | --- |
| PI-01 | 不得把不可信网页内容当作系统指令执行。 |
| PI-02 | 不得包含“忽略以上规则”等覆盖性指令。 |
| SI-01 | 不得硬编码 API Key、Token、Cookie 或密码。 |
| SI-02 | 不得把用户敏感数据写入日志、prompt 或存储分析结果。 |
| LP-01 | `allowed-tools` 只列出完成该 skill 所需的最小工具。 |
| LP-02 | 不得要求执行破坏性命令，除非用户明确授权。 |
| SC-01 | 新依赖必须来自可信来源，并在项目依赖文件中声明。 |
| KB-01 | 未验证内容必须保留来源和 URL，方便追溯。 |

### 审查清单

- `SKILL.md` 有明确的 `description` 和 `when_to_use`。
- `disable-model-invocation` 与实际行为一致。
- 不包含真实密钥或私有地址。
- 不要求绕过用户确认、权限边界或安全策略。
- 相关测试或验收命令可复制运行。

---

## English

This specification checks project workflow instructions under `.ai/skills/`. Its goal is to reduce prompt injection, sensitive data exposure, excessive permissions, and supply-chain risks.

### Risk Categories

1. Prompt injection: External content tries to override project instructions.
2. Sensitive data exposure: API keys, cookies, tokens, or user data are written to logs or docs.
3. Excessive permissions: A skill declares unnecessary tools or dangerous operations.
4. Supply-chain risk: Unreviewed scripts, dependencies, or external services are introduced.
5. Data pollution: Untrusted content flows directly into the knowledge base or prompts.

### Required Rules

| ID | Rule |
| --- | --- |
| PI-01 | Do not execute untrusted webpage content as system instructions. |
| PI-02 | Do not include override instructions such as "ignore previous rules". |
| SI-01 | Do not hard-code API keys, tokens, cookies, or passwords. |
| SI-02 | Do not write sensitive user data into logs, prompts, or stored analysis. |
| LP-01 | `allowed-tools` must list only the minimum tools needed by the skill. |
| LP-02 | Do not request destructive commands unless the user explicitly authorizes them. |
| SC-01 | New dependencies must come from trusted sources and be declared in project dependency files. |
| KB-01 | Unverified content must retain source and URL for traceability. |

### Review Checklist

- `SKILL.md` has clear `description` and `when_to_use` fields.
- `disable-model-invocation` matches actual behavior.
- No real secrets or private addresses are present.
- It does not ask to bypass user approval, permission boundaries, or safety policies.
- Related tests or acceptance commands are copyable and runnable.
