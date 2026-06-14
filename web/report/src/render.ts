import type { ReportArticle, ReportPayload } from "./types";

type BoardName = "general" | "academic";

export function renderReport(root: HTMLElement, payload: ReportPayload): void {
  root.replaceChildren();
  root.appendChild(header(payload));
  root.appendChild(tabs());

  const general = board("general", "技术资讯", payload.general);
  const academic = board("academic", "学术论文", payload.academic);
  academic.classList.add("hidden");
  root.append(general, academic);

  root.querySelectorAll<HTMLButtonElement>("[data-tab]").forEach((button) => {
    button.addEventListener("click", () => activateTab(root, button.dataset.tab as BoardName));
  });
}

export function renderError(root: HTMLElement, message: string): void {
  root.replaceChildren();
  const box = el("section", "error");
  box.appendChild(textEl("h1", "报告数据加载失败"));
  box.appendChild(textEl("p", message));
  root.appendChild(box);
}

function header(payload: ReportPayload): HTMLElement {
  const section = el("section", "hero");
  section.appendChild(textEl("h1", `AI 前沿知识日报 ${payload.date}`));
  section.appendChild(textEl("p", `生成时间：${formatDateTime(payload.generated_at)}`));
  const stats = el("div", "stats");
  [
    ["总加载", payload.stats.total_loaded],
    ["入选", payload.stats.selected],
    ["技术资讯", payload.stats.general],
    ["学术论文", payload.stats.academic],
    ["过期过滤", payload.stats.filtered_expired],
    ["低分过滤", payload.stats.filtered_low_score],
    ["资讯有效期", `${payload.filters.general_valid_days}天`],
    ["论文有效期", `${payload.filters.academic_valid_days}天`]
  ].forEach(([label, value]) => stats.appendChild(textEl("span", `${label}：${value}`)));
  section.appendChild(stats);
  return section;
}

function tabs(): HTMLElement {
  const nav = el("nav", "tabs");
  const general = textEl("button", "技术资讯");
  general.dataset.tab = "general";
  general.classList.add("active");
  const academic = textEl("button", "学术论文");
  academic.dataset.tab = "academic";
  nav.append(general, academic);
  return nav;
}

function activateTab(root: HTMLElement, tab: BoardName): void {
  root.querySelectorAll<HTMLButtonElement>("[data-tab]").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });
  root.querySelectorAll<HTMLElement>("[data-board]").forEach((section) => {
    section.classList.toggle("hidden", section.dataset.board !== tab);
  });
}

function board(name: BoardName, title: string, articles: ReportArticle[]): HTMLElement {
  const section = el("section", "board");
  section.dataset.board = name;
  section.appendChild(textEl("h2", title));
  if (articles.length === 0) {
    section.appendChild(textEl("p", "暂无入选文章", "empty"));
    return section;
  }
  articles.forEach((article, index) => section.appendChild(card(article, index + 1)));
  return section;
}

function card(article: ReportArticle, rank: number): HTMLElement {
  const node = el("article", "card");
  const head = el("div", "card-head");
  head.append(
    textEl("span", `#${rank}`, "rank"),
    textEl("span", article.rank_score.toFixed(1), "score"),
    textEl("span", article.freshness.label, article.freshness.is_valid ? "freshness" : "freshness expired")
  );
  node.appendChild(head);

  const title = textEl("h3", "");
  const link = textEl("a", article.title);
  link.setAttribute("href", article.url);
  link.setAttribute("target", "_blank");
  link.setAttribute("rel", "noreferrer");
  title.appendChild(link);
  node.appendChild(title);

  const age = article.freshness.age_days === null ? "发表时间未知" : `发表 ${article.freshness.age_days} 天`;
  node.appendChild(textEl("p", `${article.source} ｜ ${article.publish_date || "未知日期"} ｜ ${age} ｜ 有效期 ${article.freshness.valid_days} 天`, "meta"));
  node.append(tagGroup("行业", article.tags.industries), tagGroup("技术", article.tags.technologies), tagGroup("类型", article.tags.content_types));
  node.appendChild(summary(article));
  node.appendChild(textEl("p", `原始摘要：${article.abstract || "暂无摘要"}`, "abstract"));
  node.appendChild(textEl("p", article.rank_reason, "reason"));
  node.appendChild(breakdown(article.score_breakdown));
  const source = textEl("a", "原文链接", "source-link");
  source.setAttribute("href", article.url);
  source.setAttribute("target", "_blank");
  source.setAttribute("rel", "noreferrer");
  const sourceWrap = el("p");
  sourceWrap.appendChild(source);
  node.appendChild(sourceWrap);
  return node;
}

function summary(article: ReportArticle): HTMLElement {
  const box = el("div", "summary");
  box.appendChild(textEl("p", `一句话总结：${article.summary.one_sentence}`));
  box.appendChild(textEl("p", `为什么值得关注：${article.summary.why_it_matters}`));
  const label = textEl("strong", "关键要点：");
  const list = el("ul");
  article.summary.key_points.forEach((point) => list.appendChild(textEl("li", point)));
  const wrap = el("div");
  wrap.append(label, list);
  box.appendChild(wrap);
  return box;
}

function tagGroup(label: string, values: string[]): HTMLElement {
  const group = el("div", "tags");
  group.appendChild(textEl("span", label, "tag-label"));
  values.forEach((value) => group.appendChild(textEl("span", value, "tag")));
  return group;
}

function breakdown(values: Record<string, number>): HTMLElement {
  const details = el("details");
  details.appendChild(textEl("summary", "分项评分"));
  const list = el("ul");
  Object.entries(values).forEach(([key, value]) => list.appendChild(textEl("li", `${key}: ${value}`)));
  details.appendChild(list);
  return details;
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN");
}

function el<K extends keyof HTMLElementTagNameMap>(tag: K, className?: string): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  return node;
}

function textEl<K extends keyof HTMLElementTagNameMap>(tag: K, text: string, className?: string): HTMLElementTagNameMap[K] {
  const node = el(tag, className);
  node.textContent = text;
  return node;
}
