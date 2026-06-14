# AI 前沿知识信息源档案

本文档记录了项目需要爬取的所有 AI 前沿知识信息源的详细特征，包括 URL 结构、DOM 特征、更新频率、最佳 Fetcher 类型、内容质量评分等。供爬虫开发和信息源配置决策参考。

---

## 一、S级信息源（原始研究发布，技术深度最高）

### 1. ArXiv AI 论文

- **URL**: `https://arxiv.org/list/cs.AI`（分类列表）, `https://export.arxiv.org/api/query`（API接口）
- **内容类型**: 论文预印本（PDF + 元数据XML）
- **主要输出**: 每日新增 AI 论文，覆盖 LLM、多模态、强化学习、AI 安全等所有子领域
- **更新频率**: 每日（工作日更新）
- **DOM/API 特征**:
  - 列表页：静态 HTML，CSS `.list-title` / `.mathjax` 提取标题和摘要
  - API：返回 XML 格式，`<entry>` / `<title>` / `<summary>` / `<link>` 标签
  - PDF：`https://arxiv.org/pdf/{arxiv_id}.pdf`
- **最佳 Fetcher**: Fetcher（API XML），AsyncFetcher（批量 PDF 下载）
- **代理需求**: 需代理
- **技术深度**: 10/10 | **时效性**: 10/10 | **总评分**: 9.5
- **爬取策略建议**: 使用 ArXiv API 接口获取每日新论文元数据，筛选 cs.AI/cs.CL/cs.LG 分类，下载高热度论文 PDF

### 2. Anthropic Research

- **URL**: `https://www.anthropic.com/research`
- **内容类型**: 研究博客（HTML）
- **主要输出**: AI 对齐研究、可解释性分析、宪法 AI、安全对齐方法论、模型行为研究报告
- **更新频率**: 每周 1-2 篇
- **DOM 特征**: 文章列表页静态渲染，详情页 `h1` 标题 + `div.prose` 正文 + `time` 日期
- **最佳 Fetcher**: Fetcher（静态 HTML）
- **代理需求**: 需代理
- **技术深度**: 10/10 | **时效性**: 8/10 | **总评分**: 9.0
- **爬取策略建议**: 爬取研究列表页提取文章链接，逐篇爬取详情页解析 title/content/author/date

### 3. OpenAI Blog

- **URL**: `https://openai.com/blog`
- **内容类型**: 研究博客 + 产品公告（HTML，部分 JS 动态）
- **主要输出**: 新模型发布技术报告（GPT 系列）、API 更新说明、安全研究、研究论文解读
- **更新频率**: 每周 2-4 篇
- **DOM 特征**: 列表页 JS 动态加载（需 DynamicFetcher），详情页静态渲染
- **最佳 Fetcher**: DynamicFetcher（列表页）→ Fetcher（详情页）
- **代理需求**: 需代理
- **技术深度**: 9/10 | **时效性**: 9/10 | **总评分**: 9.0
- **爬取策略建议**: DynamicFetcher 获取列表页文章链接，Fetcher 爬取详情页

---

## 二、A级信息源（高质量技术内容）

### 4. DeepMind Blog

- **URL**: `https://deepmind.google/blog/`
- **内容类型**: 研究博客（HTML）
- **主要输出**: 强化学习突破、AlphaFold/科学 AI、Gemini 模型研究、多模态融合、机器人学习
- **更新频率**: 每周 2-3 篇
- **DOM 特征**: 文章列表静态 HTML，详情页标准博客结构
- **最佳 Fetcher**: Fetcher（主选）→ StealthyFetcher（被 Cloudflare 阻止时后备）
- **代理需求**: 需代理
- **技术深度**: 9/10 | **时效性**: 8/10 | **总评分**: 8.5
- **爬取策略建议**: 先用 Fetcher 尝试，遇 Cloudflare 则切换 StealthyFetcher

### 5. HuggingFace Blog

- **URL**: `https://huggingface.co/blog`
- **内容类型**: 技术 + 社区博客（HTML）
- **主要输出**: 开源模型发布（SmolVLM 等）、训练技巧、Transformers/Datasets 库更新、社区项目展示
- **更新频率**: 每周 3-5 篇
- **DOM 特征**: 列表页静态 HTML，详情页 `h1` 标题 + `div.prose` 正文 + `.author-link` 作者
- **最佳 Fetcher**: Fetcher（静态 HTML）
- **代理需求**: 需代理
- **技术深度**: 8/10 | **时效性**: 9/10 | **总评分**: 8.5
- **爬取策略建议**: Fetcher 爬取列表页和详情页，CSS 选择器提取结构化数据

### 6. Semantic Scholar

- **URL**: `https://api.semanticscholar.org/graph/v1/paper/search`（API接口）
- **内容类型**: 学术论文元数据（JSON API）
- **主要输出**: AI 驱动论文搜索、影响力评分（citation count）、引用图谱、趋势追踪、TLDR 概要
- **更新频率**: 实时更新
- **API 特征**: JSON 格式，字段 `paperId` / `title` / `abstract` / `citationCount` / `tldr` / `year`
- **最佳 Fetcher**: Fetcher（JSON API）
- **代理需求**: 需代理
- **技术深度**: 9/10 | **时效性**: 8/10 | **总评分**: 8.5
- **爬取策略建议**: 通过 API 搜索热门 AI 论文，提取 title/abstract/citationCount/tldr，按影响力排序

### 7. HuggingFace Daily Papers

- **URL**: `https://huggingface.co/papers`
- **内容类型**: 论文热度排行（HTML + JSON API）
- **主要输出**: 社区热度论文排行、关联模型和数据集、upvote 数、每日精选推荐
- **更新频率**: 每日
- **DOM/API 特征**: 页面动态加载，但 `/api/daily_papers` 返回 JSON 数据
- **最佳 Fetcher**: Fetcher（JSON API）
- **代理需求**: 需代理
- **技术深度**: 8/10 | **时效性**: 9/10 | **总评分**: 8.5
- **爬取策略建议**: 直接调用 JSON API 获取每日热门论文数据，含热度分数和社区评价

### 8. The Gradient

- **URL**: `https://thegradient.pub`
- **内容类型**: 深度分析长文（HTML）
- **主要输出**: 论文深度解读（非简单摘要）、AI 哲学反思、行业趋势长文分析、技术特稿
- **更新频率**: 每月 2-4 篇（低频高质）
- **DOM 特征**: 标准博客结构，长文深度内容
- **最佳 Fetcher**: Fetcher（静态 HTML）
- **代理需求**: 需代理
- **技术深度**: 9/10 | **时效性**: 6/10 | **总评分**: 8.0
- **爬取策略建议**: 低频高质量源，每月检查新文章即可，重点关注深度解读类内容

---

## 三、B级信息源 — 国内中文源

### 9. 机器之心

- **URL**: `https://www.jiqizhixin.com/`
- **内容类型**: 中文 AI 新闻 + 技术解读（JS 动态页面）
- **主要输出**: 国内外 AI 研究中文报道、论文解读翻译、产业动态追踪、技术教程、AI 人物专访
- **更新频率**: 每日 5-10 篇
- **DOM 特征**: 前端 React SPA，文章列表 JS 动态加载，API 接口可能返回 JSON
- **最佳 Fetcher**: DynamicFetcher（列表页 JS 渲染）或直接调用内部 API
- **代理需求**: 不需代理（国内直达）
- **技术深度**: 7/10 | **时效性**: 9/10 | **总评分**: 8.0
- **爬取策略建议**: 优先尝试内部 JSON API，其次用 DynamicFetcher 渲染列表页

### 10. 量子位

- **URL**: `https://www.qbitai.com/`
- **内容类型**: 中文 AI 快讯 + 行业分析（HTML/JS）
- **主要输出**: AI 产品发布追踪、行业资本动向、技术新闻快报、AI 工具推荐
- **更新频率**: 每日 8-15 篇
- **DOM 特征**: WordPress 系站点，文章 URL 格式 `qbitai.com/YYYY/MM/{id}.html`
- **最佳 Fetcher**: Fetcher（静态 HTML，WordPress 系通常静态渲染）
- **代理需求**: 不需代理
- **技术深度**: 6/10 | **时效性**: 9/10 | **总评分**: 7.5
- **爬取策略建议**: Fetcher 爬取主页和文章详情，CSS 选择器提取标题和正文

### 11. 智源社区

- **URL**: `https://hub.baai.ac.cn/`
- **内容类型**: 学术社区 + 论文解读（HTML）
- **主要输出**: BAAI 研究成果发布、学术论文中文解读、开源项目推荐、社区讨论精华
- **更新频率**: 每日 3-5 篇
- **DOM 特征**: 标准 CMS 系站点，静态渲染为主
- **最佳 Fetcher**: Fetcher（静态 HTML）
- **代理需求**: 不需代理
- **技术深度**: 7/10 | **时效性**: 7/10 | **总评分**: 7.5
- **爬取策略建议**: Fetcher 直接爬取，关注论文解读和开源项目类内容

---

## 四、B级信息源 — 国际行业源

### 12. Google AI Blog

- **URL**: `https://ai.googleblog.com/`
- **内容类型**: 研究 + 产品技术博客（HTML）
- **主要输出**: 搜索+AI 技术、TPU 系统研究、大规模基础模型、TensorFlow/JAX 更新
- **更新频率**: 每周 1-2 篇
- **DOM 特征**: Blogger 平台，标准 HTML 结构
- **最佳 Fetcher**: Fetcher（静态 HTML）
- **代理需求**: 需代理
- **技术深度**: 8/10 | **时效性**: 7/10 | **总评分**: 7.5
- **爬取策略建议**: Blogger 平台标准结构，CSS 选择器 `.post-title` / `.post-body` 提取

### 13. Meta AI Blog

- **URL**: `https://ai.meta.com/blog/`
- **内容类型**: 研究 + 开源发布博客（HTML/JS）
- **主要输出**: LLaMA 系列模型发布、开源 LLM 研究、多模态/视频理解、AR/VR+AI
- **更新频率**: 每周 1-2 篇
- **DOM 特征**: 现代 Web 站点，部分 JS 动态加载
- **最佳 Fetcher**: Fetcher 或 DynamicFetcher
- **代理需求**: 需代理
- **技术深度**: 8/10 | **时效性**: 7/10 | **总评分**: 7.5
- **爬取策略建议**: 先用 Fetcher 尝试，如果内容不完整则切换 DynamicFetcher

### 14. MIT Technology Review (AI Section)

- **URL**: `https://www.technologyreview.com/topic/artificial-intelligence/`
- **内容类型**: 深度产业分析（HTML）
- **主要输出**: AI 十大突破技术评选、伦理与政策讨论、产业趋势预测、深度调查报道
- **更新频率**: 每周 2-3 篇（AI 相关）
- **DOM 特征**: 标准 CMS 结构，文章有 paywall（部分需付费）
- **最佳 Fetcher**: Fetcher（静态 HTML，免费部分）
- **代理需求**: 需代理
- **技术深度**: 7/10 | **时效性**: 7/10 | **总评分**: 7.0
- **爬取策略建议**: 只爬取免费可见内容，paywall 文章标记但不强行突破

---

## 爬取优先级排序

按信息价值和技术深度综合排序：

| 优先级 | 信息源 | 核心价值 | 爬取难度 |
|--------|--------|---------|---------|
| P0 | ArXiv AI 论文 | 一手研究资料，覆盖最全 | 中（API+PDF） |
| P0 | Anthropic Research | AI 安全对齐一手研究 | 低（静态HTML） |
| P0 | OpenAI Blog | 模型发布一手技术报告 | 中（JS动态） |
| P1 | DeepMind Blog | 强化学习/科学AI一手研究 | 低（静态，需防反爬） |
| P1 | HuggingFace Blog | 开源模型社区动态 | 低（静态HTML） |
| P1 | HuggingFace Daily Papers | 社区热度论文排行 | 低（JSON API） |
| P1 | Semantic Scholar | 论文影响力评估 | 低（JSON API） |
| P2 | 机器之心 | 中文AI研究翻译解读 | 高（JS动态） |
| P2 | 量子位 | 中文AI快讯时效性强 | 低（WordPress静态） |
| P2 | 智源社区 | 中文学术社区解读 | 低（静态HTML） |
| P3 | The Gradient | 深度长文解读（低频高质） | 低（静态HTML） |
| P3 | Google AI Blog | 搜索+AI技术研究 | 低（Blogger静态） |
| P3 | Meta AI Blog | LLaMA开源LLM研究 | 中（部分JS） |
| P3 | MIT Tech Review | 产业趋势+伦理分析 | 低（静态，有paywall） |

---

## 代理需求分类

- **需代理（国外源）**: ArXiv, Anthropic, OpenAI, DeepMind, HuggingFace, Semantic Scholar, HF Daily Papers, The Gradient, Google AI, Meta AI, MIT Tech Review
- **不需代理（国内源）**: 机器之心, 量子位, 智源社区

---

## 内容类型分类

- **纯 HTML 博客**: Anthropic, DeepMind, HuggingFace Blog, The Gradient, Google AI, 量子位, 智源社区
- **JS 动态页面**: OpenAI Blog(列表页), 机器之心, Meta AI(部分)
- **JSON API**: Semantic Scholar, HuggingFace Daily Papers
- **XML API + PDF**: ArXiv
- **有 Paywall**: MIT Tech Review（部分内容）