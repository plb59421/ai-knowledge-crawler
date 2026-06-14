# Skill 安全性校验规范

基于 Anthropic Claude Code 安全文档、OWASP LLM Top 10、Agent-Threat-Rule 等行业标准制定。

## 1. 提示注入防御（Prompt Injection Defense）

### OWASP LLM01: 提示注入

**风险**：攻击者通过恶意文本覆盖或操纵 Agent 指令，使 Skill 执行非预期操作。

**校验规则**：

| 编号 | 规则 | 级别 |
|------|------|------|
| PI-01 | SKILL.md 内容不得包含可被外部文本覆盖的动态指令（如 `!`command`` 注入来自不可信源的数据） | 必须 |
| PI-02 | Skill 不应直接处理来自用户输入的原始文本并将其作为指令执行 | 必须 |
| PI-03 | 使用 `allowed-tools` 限制 Skill 可用的工具范围，防止通过注入获取额外权限 | 必须 |
| PI-04 | 动态上下文注入（`` !`command` ``）的命令必须是确定性、不可被外部操控的 | 推荐 |
| PI-05 | 禁止 Skill 内容中包含"忽略以上指令"、"无视用户设定"等覆盖性指令 | 必须 |

### Anthropic 防护措施对照

- **权限系统**：敏感操作需明确批准 → Skill 使用 `allowed-tools` 白名单
- **上下文感知分析**：检测潜在有害指令 → Skill description 明确限定触发范围
- **命令黑名单**：默认阻止 `curl`、`wget` 等风险命令 → `disallowed-tools` 限制
- **隔离的上下文窗口**：Web 内容使用独立窗口 → `context: fork` 隔离运行

## 2. 敏感信息泄露防护（Sensitive Information Disclosure）

### OWASP LLM02: 敏感信息泄露

**风险**：Skill 可能泄露 API 密钥、用户数据、系统凭证等敏感信息。

**校验规则**：

| 编号 | 规则 | 级别 |
|------|------|------|
| SI-01 | SKILL.md 不得硬编码 API 密钥、Token、密码等凭证 | 必须 |
| SI-02 | Skill 不得将用户输入的敏感数据输出到日志或外部服务 | 必须 |
| SI-03 | MCP 配置中的凭证应使用环境变量引用（如 `$GITHUB_PAT`），不得硬编码 | 必须 |
| SI-04 | `.gitignore` 必须包含 `.qoder/` 规则防止配置文件被提交 | 必须 |
| SI-05 | Skill 不得收集或存储用户浏览器 Cookie、SSH 密钥等敏感数据 | 必须 |

### 凭证管理最佳实践

- **代理模式**：凭证通过外部代理注入，Agent 不直接接触凭证
- **环境变量**：凭证通过 `env` 配置传递，而非写入 SKILL.md
- **最小权限**：凭证仅授予 Skill 所需的最小权限范围

## 3. 权限最小化（Least Privilege）

### Anthropic 安全原则对照

**风险**：Skill 权限过大可能导致意外操作或被利用执行危险命令。

**校验规则**：

| 编号 | 规则 | 级别 |
|------|------|------|
| LP-01 | `allowed-tools` 应仅列出 Skill 完成其功能所必需的工具 | 必须 |
| LP-02 | 禁止在 `allowed-tools` 中包含 `Bash(*)` 等无限制权限 | 必须 |
| LP-03 | 使用 `paths` 限制 Skill 仅在特定文件范围内激活 | 推荐 |
| LP-04 | 有副作用的 Skill（如部署、发送消息）应设置 `disable-model-invocation: true` | 必须 |
| LP-05 | Skill 不应执行 `rm -rf /`、`sudo`、`eval` 等危险命令 | 必须 |

## 4. 供应链安全（Supply Chain Vulnerabilities）

### OWASP LLM05: 供应链漏洞

**风险**：Skill 依赖的第三方包、MCP 服务器可能包含恶意代码。

**校验规则**：

| 编号 | 规则 | 级别 |
|------|------|------|
| SS-01 | Skill 使用的 Python/npm 包应为知名、维护活跃的包 | 推荐 |
| SS-02 | MCP 服务器应来自信任的提供商或自行编写 | 必须 |
| SS-03 | Skill 目录中不应包含未经审查的可执行脚本 | 必须 |
| SS-04 | 依赖版本应锁定，避免自动升级引入漏洞 | 推荐 |

## 5. 数据投毒防护（Data Poisoning）

### OWASP LLM03: 训练数据投毒

**风险**：Skill 接触的数据源可能被恶意修改，导致 Agent 输出偏移。

**校验规则**：

| 编号 | 规则 | 级别 |
|------|------|------|
| DP-01 | Skill 不应依赖单一不可信数据源作为核心决策依据 | 推荐 |
| DP-02 | 爬虫类 Skill 应验证数据完整性，对异常数据降级处理 | 推荐 |

## 6. 不当输出处理（Inadequate Output Handling）

### OWASP LLM06: 不当输出处理

**风险**：Skill 生成的输出可能包含恶意代码、SQL 注入、XSS 等危险内容。

**校验规则**：

| 编号 | 规则 | 级别 |
|------|------|------|
| OH-01 | Skill 生成可执行代码时应提示用户审查后再执行 | 必须 |
| OH-02 | Skill 不得自动执行来自网页抓取的原始代码片段 | 必须 |
| OH-03 | Skill 输出到文件的内容应经过基本安全过滤 | 推荐 |

## 7. Skill 标准性校验（Skill Standards Compliance）

基于 Claude Code 官方 Skill 规范（参考 `skill-authoring` Skill）。

**校验规则**：

| 编号 | 规则 | 级别 |
|------|------|------|
| SC-01 | SKILL.md 必须使用 YAML frontmatter 格式（`---` 标记） | 必须 |
| SC-02 | frontmatter 必须包含 `description` 字段 | 必须 |
| SC-03 | `description` + `when_to_use` 组合不超过 1536 字符 | 必须 |
| SC-04 | SKILL.md 总长度不超过 500 行 | 必须 |
| SC-05 | Skill 目录以 `SKILL.md` 为入口，辅助文件放在 `assets/` 或其他子目录 | 必须 |
| SC-06 | 从 SKILL.md 中引用支持文件，以便 Agent 知道何时加载 | 推荐 |
| SC-07 | 导入路径使用 `from scrapling import` 等标准方式，而非内部模块路径 | 推荐 |

## 8. Agent-Threat-Rule 对照

Agent-Threat-Rule 311 条规则覆盖 9 大威胁类别，与本项目相关的核心规则：

| 威胁类别 | 核心防护 | Skill 校验要点 |
|----------|----------|---------------|
| 提示注入 | 输入净化、权限限制 | PI-01 ~ PI-05 |
| 工具滥用 | 工具白名单、命令黑名单 | LP-01 ~ LP-05 |
| 数据泄露 | 凭证隔离、输出过滤 | SI-01 ~ SI-05 |
| 权限提升 | 最小权限、sandbox | LP-01 ~ LP-05 |
| 资源耗尽 | 速率控制、超时限制 | Skill 中的 delay/timeout 配置 |

## 参考来源

- [Anthropic Claude Code 安全文档](https://code.claude.com/docs/zh-CN/security)
- [Anthropic 安全部署指南](https://code.claude.com/docs/zh-CN/agent-sdk/secure-deployment)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Agent-Threat-Rule](https://github.com/Agent-Threat-Rule/ATR)
- [OpenClaw 安全使用实践指南](https://www.chinanews.com/gn/2026/03-22/10591004.shtml)