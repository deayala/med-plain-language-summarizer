export interface ReadabilityMetrics {
  flesch_reading_ease: number | null;
  flesch_kincaid_grade: number | null;
  coleman_liau_index: number | null;
  gunning_fog: number | null;
  smog_index: number | null;
  dale_chall_score: number | null;
  avg_words_per_sentence: number | null;
  compression_ratio: number | null;
  number_recall: number | null;
  repetition_ratio: number | null;
  jargon_density: number | null;
}

export interface ReadabilityBreakdown {
  source: ReadabilityMetrics;
  generated: ReadabilityMetrics;
}

export interface SummaryResponse {
  summary: string;
  latency_ms: number;
  generator: 'gpu' | 'cpu' | 'dry-run' | 'hf-endpoint';
  readability: ReadabilityBreakdown;
  generated_at: string;
}
