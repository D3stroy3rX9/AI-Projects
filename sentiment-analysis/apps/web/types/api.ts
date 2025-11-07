/**
 * API Types
 * TypeScript types generated from OpenAPI spec
 */

export type SentimentLabel = 'positive' | 'neutral' | 'negative';

export type TimeInterval = 'hour' | 'day' | 'week' | 'month';

export type TrainingStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface AnalyzeRequest {
  text: string;
}

export interface SentimentScores {
  positive: number;
  neutral: number;
  negative: number;
}

export interface EmotionScores {
  joy?: number;
  anger?: number;
  sadness?: number;
  surprise?: number;
  fear?: number;
  love?: number;
}

export interface TopWord {
  word: string;
  weight: number;
}

export interface Explanation {
  top_words: TopWord[];
}

export interface SentimentResult {
  text: string;
  sentiment: SentimentScores;
  emotion?: EmotionScores;
  explanation?: Explanation;
  confidence: number;
  predicted_label: SentimentLabel;
}

export interface BatchAnalyzeRequest {
  texts: string[];
}

export interface BatchAnalyzeResponse {
  results: SentimentResult[];
  total: number;
}

export interface SentimentDistribution {
  positive: number;
  neutral: number;
  negative: number;
}

export interface TrendPoint {
  timestamp: string;
  avg_sentiment: number;
  count: number;
  distribution: SentimentDistribution;
}

export interface TrendsResponse {
  trends: TrendPoint[];
  interval: TimeInterval;
}

export interface AnalyticsSummary {
  total_analyzed: number;
  avg_sentiment: number;
  distribution: SentimentDistribution;
  top_positive_words: string[];
  top_negative_words: string[];
}

export interface TrainingJobResponse {
  job_id: string;
  status: TrainingStatus;
  message: string;
}

export interface ModelInfo {
  id: number;
  name: string;
  version: string;
  algorithm: string;
  f1_score: number;
  training_samples: number;
  vocabulary_size: number;
  created_at: string;
  is_active: boolean;
}

export interface F1Scores {
  positive: number;
  neutral: number;
  negative: number;
  overall: number;
}

export interface FeatureImportance {
  positive: TopWord[];
  negative: TopWord[];
}

export interface ModelEvaluation {
  model_id: number;
  confusion_matrix: number[][];
  f1_scores: F1Scores;
  feature_importance: FeatureImportance;
}

export interface Error {
  error: string;
  detail?: string;
}

export interface ValidationErrorDetail {
  loc: string[];
  msg: string;
  type: string;
}

export interface ValidationError {
  detail: ValidationErrorDetail[];
}

export interface WebhookResponse {
  received: boolean;
  sentiment_result?: SentimentResult;
}

// API Query Parameters
export interface TrendsParams {
  start_date?: string;
  end_date?: string;
  interval?: TimeInterval;
  limit?: number;
}

export interface SummaryParams {
  start_date?: string;
  end_date?: string;
}
