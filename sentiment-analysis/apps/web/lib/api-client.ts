/**
 * API Client
 * Type-safe API client for Sentiment Analysis API
 */

import type {
  AnalyzeRequest,
  SentimentResult,
  BatchAnalyzeRequest,
  BatchAnalyzeResponse,
  TrendsResponse,
  TrendsParams,
  AnalyticsSummary,
  SummaryParams,
  ModelInfo,
  ModelEvaluation,
  TrainingJobResponse,
} from '../types/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: 'Request failed',
        detail: response.statusText,
      }));
      throw new Error(error.detail || error.error || 'Request failed');
    }

    return response.json();
  }

  // Analysis endpoints
  async analyze(request: AnalyzeRequest): Promise<SentimentResult> {
    return this.request<SentimentResult>('/analyze', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async analyzeBatch(
    request: BatchAnalyzeRequest
  ): Promise<BatchAnalyzeResponse> {
    return this.request<BatchAnalyzeResponse>('/analyze/batch', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Analytics endpoints
  async getTrends(params?: TrendsParams): Promise<TrendsResponse> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<TrendsResponse>(
      `/analytics/trends${query ? `?${query}` : ''}`
    );
  }

  async getSummary(params?: SummaryParams): Promise<AnalyticsSummary> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<AnalyticsSummary>(
      `/analytics/summary${query ? `?${query}` : ''}`
    );
  }

  // Model management endpoints
  async listModels(): Promise<ModelInfo[]> {
    return this.request<ModelInfo[]>('/models');
  }

  async evaluateModel(modelId: number): Promise<ModelEvaluation> {
    return this.request<ModelEvaluation>(`/models/${modelId}/evaluate`);
  }

  async trainModel(file: File, name?: string): Promise<TrainingJobResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (name) {
      formData.append('name', name);
    }

    const response = await fetch(`${this.baseUrl}/models/train`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: 'Upload failed',
      }));
      throw new Error(error.detail || error.error || 'Upload failed');
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
