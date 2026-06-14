"""Chinese article tagging."""

from src.core.models import Article


INDUSTRY_KEYWORDS = {
    "医疗": ["医疗", "医学", "药物", "临床", "基因", "生命科学", "health", "medical", "drug", "genomics"],
    "金融": ["金融", "银行", "投研", "风控", "交易", "finance", "bank"],
    "教育": ["教育", "学习", "教学", "课程", "学生", "education"],
    "制造": ["制造", "工厂", "工业", "供应链", "manufacturing"],
    "机器人": ["机器人", "robot", "robotics"],
    "自动驾驶": ["自动驾驶", "autonomous driving", "self-driving"],
    "游戏": ["游戏", "game", "gaming"],
    "科研": ["科研", "科学", "论文", "研究", "science", "research", "arxiv"],
    "企业服务": ["企业", "办公", "workflow", "saas", "enterprise"],
    "云计算": ["云", "cloud", "serverless", "kubernetes"],
    "芯片": ["芯片", "gpu", "tpu", "h100", "算力", "chip"],
    "安全": ["安全", "对齐", "红队", "security", "safety", "alignment"],
    "媒体内容": ["视频", "图像", "音频", "媒体", "生成内容", "media"],
    "开发者工具": ["代码", "开发者", "api", "github", "codex", "developer", "tool"],
}

TECH_KEYWORDS = {
    "LLM": ["llm", "large language model", "大语言模型", "大模型"],
    "VLM": ["vlm", "vision language", "视觉语言"],
    "多模态": ["多模态", "multimodal", "image-text", "vision-language"],
    "智能体": ["智能体", "agent", "agents", "agentic"],
    "RAG": ["rag", "检索增强"],
    "微调": ["微调", "fine-tuning", "finetune", "sft"],
    "推理": ["推理", "reasoning", "inference"],
    "强化学习": ["强化学习", "reinforcement learning"],
    "RLHF": ["rlhf"],
    "对齐": ["对齐", "alignment", "safety"],
    "评测": ["评测", "evaluation", "eval", "benchmark"],
    "Benchmark": ["benchmark", "基准"],
    "长上下文": ["长上下文", "long context", "context window"],
    "记忆机制": ["记忆", "memory", "mem"],
    "工具调用": ["工具调用", "tool use", "function calling", "tool calling"],
    "代码生成": ["代码生成", "code generation", "coding", "codex"],
    "世界模型": ["世界模型", "world model"],
    "具身智能": ["具身", "embodied"],
    "语音": ["语音", "speech", "audio"],
    "视频生成": ["视频生成", "video generation"],
    "检索": ["检索", "retrieval", "search"],
    "知识图谱": ["知识图谱", "knowledge graph"],
    "模型压缩": ["压缩", "distill", "distillation", "quantization"],
    "推理加速": ["推理加速", "加速", "serving", "latency"],
    "开源模型": ["开源", "open source", "huggingface", "github"],
}

CONTENT_TYPE_KEYWORDS = {
    "学术论文": ["arxiv", "paper", "论文", "实验", "benchmark"],
    "技术博客": ["技术", "博客", "research", "blog"],
    "产品发布": ["发布", "推出", "introducing", "launch", "release"],
    "公司动态": ["收购", "融资", "合作", "公司", "acquire", "partnership"],
    "行业新闻": ["新闻", "消息", "报道"],
    "深度解读": ["解读", "分析", "路线", "为什么", "深度"],
    "访谈": ["访谈", "interview"],
    "调研报告": ["报告", "调研", "survey", "report"],
    "教程": ["教程", "指南", "how to", "course"],
    "开源项目": ["github", "开源", "代码", "weights"],
    "Benchmark": ["benchmark", "基准"],
    "案例研究": ["案例", "case study"],
}

DEFAULT_CONTENT_TYPES = {
    "arxiv": "学术论文",
    "semantic_scholar": "学术论文",
    "openalex": "学术论文",
    "qbitai": "行业新闻",
    "jiqizhixin": "行业新闻",
    "openai": "技术博客",
    "deepmind": "技术博客",
    "anthropic": "技术博客",
    "huggingface": "技术博客",
}


class ChineseTagger:
    """Generate structured Chinese tags for an Article."""

    def tag(self, article: Article) -> dict:
        text = self._text(article)
        industries = self._match(text, INDUSTRY_KEYWORDS) or ["通用"]
        technologies = self._match(text, TECH_KEYWORDS) or ["AI"]
        content_types = self._match(text, CONTENT_TYPE_KEYWORDS)
        default_type = DEFAULT_CONTENT_TYPES.get(article.source)
        if default_type and default_type not in content_types:
            content_types.insert(0, default_type)
        if not content_types:
            content_types = ["技术博客"]
        return {
            "industries": industries,
            "technologies": technologies,
            "content_types": content_types,
        }

    def _text(self, article: Article) -> str:
        analysis = article.analysis.to_dict() if article.analysis else {}
        return " ".join([
            article.source,
            article.title,
            article.abstract,
            article.full_text,
            " ".join(article.topics),
            " ".join(str(v) for v in analysis.values()),
        ]).lower()

    def _match(self, text: str, keyword_map: dict[str, list[str]]) -> list[str]:
        matched = []
        for label, keywords in keyword_map.items():
            if any(keyword.lower() in text for keyword in keywords):
                matched.append(label)
        return matched
