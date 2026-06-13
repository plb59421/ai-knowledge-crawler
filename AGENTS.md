# ai_knowledge_crawler

AI前沿知识爬虫 - 定时从多个AI技术信息渠道自动抓取最前沿的AI领域知识与技术动态。

## 项目定位

两层架构设计：

1. **AI 能力层**（`.qoder/`）：知识库参考文档、可调用的 Skill、SpringAI 风格 .st 提示词模板
2. **工程能力层**（`src/`）：爬虫执行、多格式文件整理、日志打印、存储

## 目录结构

```
ai_knowledge_crawler/
├── .qoder/
│   ├── mcp.json                                    # MCP 服务器配置
│   ├── skills/
│   │   └── web-scraping/                           # Scrapling 爬虫 Skill
│   │       └── SKILL.md
│   ├── prompts/
│   │   └── summarize.st                            # 内容摘要模板 (SpringAI 格式)
│   └── knowledge/
│       └── skill-security-spec.md                  # Skill 安全校验规范
├── config/
│   ├── settings.yaml                               # 全局设置
│   ├── sources.yaml                                # 信息源配置 (huggingface + jiqizhixin)
│   └── logging.yaml                                # 日志配置
├── src/
│   ├── core/
│   │   └── models.py                               # CrawlResult + Article 数据类
│   ├── crawlers/
│   │   ├── base.py                                 # BaseCrawler 抽象基类
│   │   ├── huggingface/
│   │   │   ├── crawler.py                           # HuggingFaceCrawler (需代理)
│   │   │   └── parser.py                            # HuggingFaceParser
│   │   └── jiqizhixin/
│   │       ├── crawler.py                           # JiqiZhixinCrawler (国内可达, JS动态页面)
│   │       └── parser.py                            # JiqiZhixinParser
│   ├── processors/
│   │   └── html_processor.py                       # HTML 清洗处理器
│   ├── storage/
│   │   └── knowledge_store.py                      # JSON 文件存储 (by_source/层级)
│   └── utils/
│       └── logger.py                               # structlog 结构化日志
├── scripts/
│   ├── run_crawler.py                              # 手动爬取 CLI (--source huggingface/jiqizhixin)
│   └── local_test.py                               # 本地流水线测试 (不依赖网络)
├── tests/
│   └── fixtures/
│       └── sample_hf_blog.html                     # HuggingFace 博客 HTML 样本
├── knowledge_base/                                  # 输出：知识仓库
│   ├── by_source/huggingface/2026/06/              # 已有存储数据
│   ├── by_topic/
│   ├── by_time/
│   ├── index/
│   └── metadata/
├── logs/
├── AGENTS.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── .env.example
```

## 技术栈

- Python >= 3.11
- Scrapling >= 0.4 (网页爬取框架)
- structlog >= 23.1 (结构化日志)
- PyYAML >= 6.0 (配置文件解析)
- BeautifulSoup4 >= 4.12 (HTML 解析备选)

## 已安装 Skill

| Skill 名称 | 位置 | 说明 | 安全校验 |
|------------|------|------|----------|
| web-scraping | .qoder/skills/web-scraping/ | Scrapling 爬虫执行 + Fetcher 选型决策 | pass |

## .st 提示词模板

| 文件 | 位置 | 说明 |
|------|------|------|
| summarize.st | .qoder/prompts/ | SpringAI 格式内容摘要模板，{raw_content}, {source_name}, {max_length}, {language} |

## 知识库

| 文件 | 位置 | 说明 |
|------|------|----------|
| skill-security-spec.md | .qoder/knowledge/ | Skill 安全校验规范（8 类 29 条规则），基于 OWASP LLM Top 10 |

## 信息源配置

| 源名称 | base_url | 代理需求 | Fetcher 类型 | 说明 |
|--------|----------|----------|--------------|------|
| huggingface | huggingface.co/blog | 需代理 | Fetcher | 需开启 Clash Verge |
| jiqizhixin | jiqizhixin.com | 不需代理 | 需 DynamicFetcher | JS动态页面，静态 Fetcher 仅获取导航骨架 |

## 运行方式

本地流水线测试（不依赖网络，验证完整流程）：
```bash
cd d:/AI_WORK_SPACE/ai_knowledge_crawler
python scripts/local_test.py
```

手动爬取（需代理才能访问 HuggingFace）：
```bash
python scripts/run_crawler.py --source huggingface
```

手动爬取机器之心（国内可达但需 DynamicFetcher）：
```bash
python scripts/run_crawler.py --source jiqizhixin --no-proxy
```

## MVP 验证结果

本地测试已通过：
- 读取 sample_hf_blog.html → Scrapling Adaptor 解析 title/content/author/date → KnowledgeStore 存入 by_source/huggingface/2026/06/2026-06-12.json
- 输出 JSON 包含 id, source, title, abstract, full_text, authors, publish_date, url

## Skill 管理原则

> **项目级优先**：所有 Skill 保存在 `.qoder/skills/` 目录下。
> **安全校验**：所有 Skill 必须通过安全性校验（参考 `.qoder/knowledge/skill-security-spec.md`）。