# AI Source Profiles

[中文](#中文) | [English](#english)

---

## 中文

本文记录当前项目维护的信息源画像，供 crawler 选型、配置调整和人工复核使用。

| source | 类型 | 代理 | 推荐抓取器 | 备注 |
| --- | --- | --- | --- | --- |
| `arxiv` | 学术论文 API | 否 | `Fetcher` | 使用 Atom XML/API metadata，论文评分走 academic profile。 |
| `openalex` | 学术元数据 API | 否 | `Fetcher` | Semantic Scholar 的替代方案，默认不需要 API Key。 |
| `huggingface` | 技术博客 | 是 | `Fetcher` | 开源模型、工具库和社区内容。 |
| `hf_daily_papers` | 论文聚合 | 是 | `Fetcher` | 默认按通用资讯处理，可后续按内容切换 academic。 |
| `openai` | 官方博客/研究 | 是 | `DynamicFetcher` | 列表页可能依赖动态渲染。 |
| `anthropic` | 官方研究博客 | 是 | `Fetcher` | 对齐、安全和模型行为研究。 |
| `deepmind` | 官方研究博客 | 是 | `Fetcher` | 科学 AI、多模态、强化学习和模型研究。 |
| `google_ai` | 官方研究博客 | 是 | `Fetcher` | 研究与产品技术更新。 |
| `meta_ai` | 官方研究博客 | 是 | `Fetcher` | 开源模型和研究发布。 |
| `qbitai` | 中文技术媒体 | 否 | `Fetcher` | 行业新闻和技术解读。 |
| `jiqizhixin` | 中文技术媒体 | 否 | `DynamicFetcher` | JS 动态页面，静态抓取可能只能得到页面骨架。 |
| `the_gradient` | 技术长文 | 否 | `Fetcher` | 深度解读和研究评论。 |
| `baai_hub` | 研究社区 | 否 | `Fetcher` | 中文研究社区和模型生态。 |
| `semantic_scholar` | 学术 API | 是 | `Fetcher` | 默认运行组禁用，后续以 `openalex` 替代。 |

### 接入原则

- 新来源必须先通过 fixture parser 测试。
- 代理源应与国内/API 源分组运行。
- 学术源和通用资讯源评分体系保持隔离。
- 不稳定来源先保留手动入口，验证稳定后再加入每日任务。

---

## English

This document records maintained source profiles for crawler selection, configuration changes, and human review.

| source | Type | Proxy | Recommended fetcher | Notes |
| --- | --- | --- | --- | --- |
| `arxiv` | Academic paper API | No | `Fetcher` | Uses Atom XML/API metadata; ranked with the academic profile. |
| `openalex` | Academic metadata API | No | `Fetcher` | Replacement for Semantic Scholar; no API key by default. |
| `huggingface` | Technical blog | Yes | `Fetcher` | Open models, libraries, and community posts. |
| `hf_daily_papers` | Paper aggregator | Yes | `Fetcher` | Defaults to general profile; may switch to academic by content later. |
| `openai` | Official blog/research | Yes | `DynamicFetcher` | Listing pages may require dynamic rendering. |
| `anthropic` | Official research blog | Yes | `Fetcher` | Alignment, safety, and model behavior research. |
| `deepmind` | Official research blog | Yes | `Fetcher` | Science AI, multimodal, reinforcement learning, and model research. |
| `google_ai` | Official research blog | Yes | `Fetcher` | Research and product technical updates. |
| `meta_ai` | Official research blog | Yes | `Fetcher` | Open models and research releases. |
| `qbitai` | Chinese technical media | No | `Fetcher` | Industry news and technical interpretation. |
| `jiqizhixin` | Chinese technical media | No | `DynamicFetcher` | JS-driven pages; static fetches may only return page skeletons. |
| `the_gradient` | Long-form technical writing | No | `Fetcher` | Deep analysis and research commentary. |
| `baai_hub` | Research community | No | `Fetcher` | Chinese research community and model ecosystem. |
| `semantic_scholar` | Academic API | Yes | `Fetcher` | Disabled from default runs; planned to be replaced by `openalex`. |

### Onboarding Principles

- New sources must pass fixture parser tests first.
- Proxy sources should run separately from domestic/API sources.
- Academic and general content must keep separate ranking profiles.
- Unstable sources should remain manual-only until validated.
