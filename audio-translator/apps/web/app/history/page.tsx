"use client";

import { useState, useEffect } from "react";
import { Trash2, Download, Search, ChevronLeft, ChevronRight, Copy, Check } from "lucide-react";
import Link from "next/link";

interface Translation {
  id: string;
  created_at: string;
  source_language: string;
  target_language: string;
  source_text: string;
  translated_text: string;
  audio_duration: number;
  confidence_score: number;
  session_id: string | null;
}

interface HistoryResponse {
  total: number;
  limit: number;
  offset: number;
  results: Translation[];
}

const LANGUAGE_NAMES: { [key: string]: string } = {
  en: "English",
  es: "Spanish",
  fr: "French",
  de: "German",
  it: "Italian",
  pt: "Portuguese",
  ru: "Russian",
  zh: "Chinese",
  ja: "Japanese",
  ko: "Korean",
  ar: "Arabic",
  hi: "Hindi",
  nl: "Dutch",
  pl: "Polish",
  tr: "Turkish",
  vi: "Vietnamese",
  th: "Thai",
  id: "Indonesian",
  sv: "Swedish",
  no: "Norwegian",
};

export default function HistoryPage() {
  const [history, setHistory] = useState<Translation[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [filterLanguage, setFilterLanguage] = useState<string>("all");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Fetch history
  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const offset = (currentPage - 1) * itemsPerPage;
      const response = await fetch(
        `${apiUrl}/history?limit=${itemsPerPage}&offset=${offset}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch history");
      }

      const data: HistoryResponse = await response.json();
      setHistory(data.results);
      setTotal(data.total);
    } catch (error) {
      console.error("Error fetching history:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [currentPage]);

  // Delete translation
  const deleteTranslation = async (id: string) => {
    if (!confirm("Are you sure you want to delete this translation?")) {
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/history/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete translation");
      }

      // Refresh history
      fetchHistory();
    } catch (error) {
      console.error("Error deleting translation:", error);
      alert("Failed to delete translation");
    }
  };

  // Clear all history
  const clearAllHistory = async () => {
    if (
      !confirm(
        "Are you sure you want to delete ALL translation history? This cannot be undone."
      )
    ) {
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/history`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to clear history");
      }

      // Refresh history
      fetchHistory();
    } catch (error) {
      console.error("Error clearing history:", error);
      alert("Failed to clear history");
    }
  };

  // Export as JSON
  const exportAsJSON = () => {
    const dataStr = JSON.stringify(history, null, 2);
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
    const exportFileDefaultName = `translation-history-${new Date().toISOString()}.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  // Export as CSV
  const exportAsCSV = () => {
    const headers = [
      "Timestamp",
      "Source Language",
      "Target Language",
      "Original Text",
      "Translated Text",
      "Confidence",
      "Duration (s)",
    ];

    const rows = history.map((t) => [
      new Date(t.created_at).toISOString(),
      t.source_language,
      t.target_language,
      `"${t.source_text.replace(/"/g, '""')}"`,
      `"${t.translated_text.replace(/"/g, '""')}"`,
      t.confidence_score,
      t.audio_duration,
    ]);

    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join(
      "\n"
    );

    const dataUri = `data:text/csv;charset=utf-8,${encodeURIComponent(csvContent)}`;
    const exportFileDefaultName = `translation-history-${new Date().toISOString()}.csv`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  // Export as TXT
  const exportAsTXT = () => {
    const content = history
      .map((t) => {
        const date = new Date(t.created_at).toLocaleString();
        return `[${date}] ${getLanguageName(t.source_language)} → ${getLanguageName(
          t.target_language
        )}\nOriginal: ${t.source_text}\nTranslation: ${t.translated_text}\n---\n`;
      })
      .join("\n");

    const dataUri = `data:text/plain;charset=utf-8,${encodeURIComponent(content)}`;
    const exportFileDefaultName = `translation-history-${new Date().toISOString()}.txt`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  // Copy text to clipboard
  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  const getLanguageName = (code: string): string => {
    return LANGUAGE_NAMES[code] || code.toUpperCase();
  };

  // Filter history based on search query and language filter
  const filteredHistory = history.filter((t) => {
    const matchesSearch =
      searchQuery === "" ||
      t.source_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.translated_text.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesLanguage =
      filterLanguage === "all" ||
      t.source_language === filterLanguage ||
      t.target_language === filterLanguage;

    return matchesSearch && matchesLanguage;
  });

  // Pagination
  const totalPages = Math.ceil(total / itemsPerPage);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Translation History
              </h1>
              <p className="text-gray-600 mt-2">
                View and manage your translation history ({total} total)
              </p>
            </div>

            <Link
              href="/"
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              ← Back to Translator
            </Link>
          </div>

          {/* Actions bar */}
          <div className="flex flex-wrap gap-4 items-center justify-between bg-white p-4 rounded-lg shadow">
            {/* Search */}
            <div className="flex-1 min-w-[200px] max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search translations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Language filter */}
            <select
              value={filterLanguage}
              onChange={(e) => setFilterLanguage(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Languages</option>
              {Object.entries(LANGUAGE_NAMES).map(([code, name]) => (
                <option key={code} value={code}>
                  {name}
                </option>
              ))}
            </select>

            {/* Export buttons */}
            <div className="flex gap-2">
              <button
                onClick={exportAsJSON}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
                disabled={history.length === 0}
              >
                <Download className="w-4 h-4" />
                JSON
              </button>
              <button
                onClick={exportAsCSV}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
                disabled={history.length === 0}
              >
                <Download className="w-4 h-4" />
                CSV
              </button>
              <button
                onClick={exportAsTXT}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
                disabled={history.length === 0}
              >
                <Download className="w-4 h-4" />
                TXT
              </button>
            </div>

            {/* Clear all button */}
            <button
              onClick={clearAllHistory}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2"
              disabled={total === 0}
            >
              <Trash2 className="w-4 h-4" />
              Clear All
            </button>
          </div>
        </div>

        {/* History list */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-500">Loading history...</div>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500">No translations found</p>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="mt-4 text-blue-500 hover:underline"
              >
                Clear search
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredHistory.map((translation) => (
              <div
                key={translation.id}
                className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-medium text-gray-600">
                        {new Date(translation.created_at).toLocaleString()}
                      </span>
                      <span className="text-sm text-gray-500">
                        {getLanguageName(translation.source_language)} →{" "}
                        {getLanguageName(translation.target_language)}
                      </span>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {Math.round(translation.confidence_score * 100)}% confident
                      </span>
                      {translation.audio_duration > 0 && (
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          {translation.audio_duration.toFixed(1)}s
                        </span>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => deleteTranslation(translation.id)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete translation"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Original text */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-gray-700">
                        Original
                      </h3>
                      <button
                        onClick={() =>
                          copyToClipboard(
                            translation.source_text,
                            `${translation.id}-source`
                          )
                        }
                        className="p-1 hover:bg-gray-100 rounded transition-colors"
                        title="Copy original text"
                      >
                        {copiedId === `${translation.id}-source` ? (
                          <Check className="w-4 h-4 text-green-600" />
                        ) : (
                          <Copy className="w-4 h-4 text-gray-600" />
                        )}
                      </button>
                    </div>
                    <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                      {translation.source_text}
                    </p>
                  </div>

                  {/* Translated text */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-gray-700">
                        Translation
                      </h3>
                      <button
                        onClick={() =>
                          copyToClipboard(
                            translation.translated_text,
                            `${translation.id}-translation`
                          )
                        }
                        className="p-1 hover:bg-gray-100 rounded transition-colors"
                        title="Copy translation"
                      >
                        {copiedId === `${translation.id}-translation` ? (
                          <Check className="w-4 h-4 text-green-600" />
                        ) : (
                          <Copy className="w-4 h-4 text-gray-600" />
                        )}
                      </button>
                    </div>
                    <p className="text-gray-900 bg-blue-50 p-3 rounded-lg font-medium">
                      {translation.translated_text}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-8 flex items-center justify-center gap-4">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-2 rounded-lg bg-white shadow hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <span className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>

            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg bg-white shadow hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
