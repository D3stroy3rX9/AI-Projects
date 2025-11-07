'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';
import type { SentimentResult } from '@/types/api';

export default function Home() {
  const [text, setText] = useState('');
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeSentiment = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await apiClient.analyze({ text });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze sentiment');
      console.error('Error analyzing sentiment:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (label: string) => {
    switch (label) {
      case 'positive':
        return 'text-green-600';
      case 'negative':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Analysis Input */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Analyze Text</h2>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to analyze sentiment...&#10;&#10;Try:&#10;• This product is absolutely fantastic!&#10;• Terrible experience, would not recommend.&#10;• The item arrived on time as expected."
          className="w-full h-40 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
        <div className="flex items-center justify-between mt-4">
          <span className="text-sm text-gray-500">
            {text.length} / 10,000 characters
          </span>
          <button
            onClick={analyzeSentiment}
            disabled={loading || !text.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Analyzing...' : 'Analyze Sentiment'}
          </button>
        </div>
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Results</h2>

          <div className="space-y-6">
            {/* Primary Sentiment */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-700">Primary Sentiment</h3>
                <span className={`text-lg font-bold capitalize ${getSentimentColor(result.predicted_label)}`}>
                  {result.predicted_label}
                </span>
              </div>
            </div>

            {/* Sentiment Scores */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Sentiment Breakdown</h3>
              <div className="space-y-3">
                {/* Positive */}
                <div className="flex items-center">
                  <span className="w-24 text-sm text-gray-600">Positive</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 relative overflow-hidden">
                    <div
                      className="bg-green-500 h-6 rounded-full transition-all duration-500"
                      style={{ width: `${result.sentiment.positive * 100}%` }}
                    />
                  </div>
                  <span className="ml-3 text-sm font-medium w-16 text-right">
                    {(result.sentiment.positive * 100).toFixed(1)}%
                  </span>
                </div>

                {/* Neutral */}
                <div className="flex items-center">
                  <span className="w-24 text-sm text-gray-600">Neutral</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 relative overflow-hidden">
                    <div
                      className="bg-gray-500 h-6 rounded-full transition-all duration-500"
                      style={{ width: `${result.sentiment.neutral * 100}%` }}
                    />
                  </div>
                  <span className="ml-3 text-sm font-medium w-16 text-right">
                    {(result.sentiment.neutral * 100).toFixed(1)}%
                  </span>
                </div>

                {/* Negative */}
                <div className="flex items-center">
                  <span className="w-24 text-sm text-gray-600">Negative</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 relative overflow-hidden">
                    <div
                      className="bg-red-500 h-6 rounded-full transition-all duration-500"
                      style={{ width: `${result.sentiment.negative * 100}%` }}
                    />
                  </div>
                  <span className="ml-3 text-sm font-medium w-16 text-right">
                    {(result.sentiment.negative * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Explanation */}
            {result.explanation && result.explanation.top_words.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  Top Influential Words
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.explanation.top_words.slice(0, 10).map((item, idx) => (
                    <span
                      key={idx}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium ${
                        item.weight > 0
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {item.word}
                      <span className="ml-1 text-xs opacity-75">
                        ({item.weight > 0 ? '+' : ''}
                        {item.weight.toFixed(2)})
                      </span>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Confidence */}
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Confidence Score</span>
                <div className="flex items-center">
                  <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">
                    {(result.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats Placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-600 mb-1">Total Analyzed</div>
          <div className="text-3xl font-bold text-gray-900">-</div>
          <div className="text-xs text-gray-500 mt-1">Coming in prompt (c)</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-600 mb-1">Avg Sentiment</div>
          <div className="text-3xl font-bold text-gray-900">-</div>
          <div className="text-xs text-gray-500 mt-1">Coming in prompt (c)</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-600 mb-1">Model F1 Score</div>
          <div className="text-3xl font-bold text-gray-900">-</div>
          <div className="text-xs text-gray-500 mt-1">Coming in prompt (f)</div>
        </div>
      </div>
    </div>
  );
}
