'use client';

import { useState } from 'react';

export default function Home() {
  const [text, setText] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const analyzeSentiment = async () => {
    if (!text.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error analyzing sentiment:', error);
    } finally {
      setLoading(false);
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
          placeholder="Enter text to analyze sentiment..."
          className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={analyzeSentiment}
          disabled={loading || !text.trim()}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {loading ? 'Analyzing...' : 'Analyze Sentiment'}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Results</h2>
          <div className="space-y-4">
            {/* Sentiment Scores */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Sentiment</h3>
              <div className="space-y-2">
                <div className="flex items-center">
                  <span className="w-24 text-sm text-gray-600">Positive:</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-green-500 h-4 rounded-full"
                      style={{ width: `${(result.sentiment?.positive || 0) * 100}%` }}
                    />
                  </div>
                  <span className="ml-2 text-sm font-medium">
                    {((result.sentiment?.positive || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="w-24 text-sm text-gray-600">Neutral:</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-gray-500 h-4 rounded-full"
                      style={{ width: `${(result.sentiment?.neutral || 0) * 100}%` }}
                    />
                  </div>
                  <span className="ml-2 text-sm font-medium">
                    {((result.sentiment?.neutral || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="w-24 text-sm text-gray-600">Negative:</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-red-500 h-4 rounded-full"
                      style={{ width: `${(result.sentiment?.negative || 0) * 100}%` }}
                    />
                  </div>
                  <span className="ml-2 text-sm font-medium">
                    {((result.sentiment?.negative || 0) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Explanation */}
            {result.explanation && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Top Influential Words
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.explanation.top_words?.slice(0, 10).map((item: any, idx: number) => (
                    <span
                      key={idx}
                      className={`px-3 py-1 rounded-full text-sm ${
                        item.weight > 0
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {item.word} ({item.weight > 0 ? '+' : ''}
                      {item.weight.toFixed(2)})
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Confidence */}
            <div>
              <span className="text-sm text-gray-600">Confidence: </span>
              <span className="text-sm font-medium">
                {((result.confidence || 0) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-600">Total Analyzed</div>
          <div className="text-2xl font-bold text-gray-900">0</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-600">Avg Sentiment</div>
          <div className="text-2xl font-bold text-gray-900">-</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-600">Model F1 Score</div>
          <div className="text-2xl font-bold text-gray-900">-</div>
        </div>
      </div>
    </div>
  );
}
