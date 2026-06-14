export interface Freshness {
  label: string;
  age_days: number | null;
  valid_days: number;
  is_valid: boolean;
}

export interface ArticleTags {
  industries: string[];
  technologies: string[];
  content_types: string[];
}

export interface ArticleSummary {
  one_sentence: string;
  why_it_matters: string;
  key_points: string[];
}

export interface ReportArticle {
  id: string;
  source: string;
  title: string;
  url: string;
  publish_date: string;
  abstract: string;
  summary: ArticleSummary;
  tags: ArticleTags;
  rank_score: number;
  score_profile: "academic" | "general" | string;
  score_breakdown: Record<string, number>;
  rank_reason: string;
  freshness: Freshness;
}

export interface ReportPayload {
  generated_at: string;
  date: string;
  stats: {
    total_loaded: number;
    selected: number;
    academic: number;
    general: number;
    filtered_expired: number;
    filtered_low_score: number;
  };
  filters: {
    profile: string;
    limit: number;
    pass_score: number | null;
    include_expired: boolean;
    general_valid_days: number;
    academic_valid_days: number;
    sources: string[];
    tag?: string;
  };
  academic: ReportArticle[];
  general: ReportArticle[];
}
