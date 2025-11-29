"use client";

import { useState, useEffect } from "react";
import { History, ChevronDown, ChevronUp, ExternalLink, Trash2 } from "lucide-react";
import Link from "next/link";

interface Translation {
  id: string;
  created_at: string;
  source_language: string;
  target_language: string;
  source_text: string;
  translated_text: string;
  confidence_score: number;
}

interface TranslationHistoryProps {
  sessionId?: string | null;
  onTranslationSelect?: (translation: Translation) => void;
  refreshTrigger?: number;
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

export default function TranslationHistory({
  sessionId,
  onTranslationSelect,
  refreshTrigger = 0,
}: TranslationHistoryProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [history, setHistory] = useState<Translation[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Fetch recent history
  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const url = sessionId
        ? `${apiUrl}/history?limit=5&session_id=${sessionId}`
        : `${apiUrl}/history?limit=5`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error("Failed to fetch history");
      }

      const data = await response.json();
      setHistory(data.results || []);
    } catch (error) {
      console.error("Error fetching history:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [sessionId, refreshTrigger]);

  // Delete translation
  const deleteTranslation = async (id: string, event: React.MouseEvent) => {
    event.stopPropagation();

    if (!confirm("Delete this translation?")) {
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
    }
  };

  const getLanguageName = (code: string): string => {
    return LANGUAGE_NAMES[code] || code.toUpperCase();
  };

  const truncateText = (text: string, maxLength: number = 80): string => {
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
  };

  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div
        className="bg-gradient-to-r from-purple-500 to-blue-500 px-4 py-3 flex items-center justify-between cursor-pointer"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center gap-2 text-white">
          <History className="w-5 h-5" />
          <h2 className="font-semibold">Recent History</h2>
          <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">
            {history.length}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/history"
            className="text-white hover:bg-white/20 p-1.5 rounded transition-colors"
            title="View all history"
            onClick={(e) => e.stopPropagation()}
          >
            <ExternalLink className="w-4 h-4" />
          </Link>

          <button
            className="text-white hover:bg-white/20 p-1.5 rounded transition-colors"
            title={isCollapsed ? "Expand" : "Collapse"}
          >
            {isCollapsed ? (
              <ChevronDown className="w-5 h-5" />
            ) : (
              <ChevronUp className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="max-h-[500px] overflow-y-auto">
          {isLoading ? (
            <div className="p-6 text-center text-gray-500">
              Loading history...
            </div>
          ) : history.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              <p className="text-sm">No translations yet</p>
              <p className="text-xs mt-1">Start recording to build your history</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {history.map((translation) => {
                const isExpanded = expandedId === translation.id;

                return (
                  <div
                    key={translation.id}
                    className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => {
                      if (onTranslationSelect) {
                        onTranslationSelect(translation);
                      }
                    }}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-gray-600">
                            {getLanguageName(translation.source_language)} →{" "}
                            {getLanguageName(translation.target_language)}
                          </span>
                          <span className="text-xs text-gray-400">
                            {formatTimeAgo(translation.created_at)}
                          </span>
                        </div>

                        <p className="text-sm text-gray-900 truncate">
                          {truncateText(translation.source_text, 60)}
                        </p>
                        <p className="text-sm text-blue-600 truncate mt-1">
                          {truncateText(translation.translated_text, 60)}
                        </p>
                      </div>

                      <div className="flex items-center gap-1 ml-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedId(isExpanded ? null : translation.id);
                          }}
                          className="p-1.5 hover:bg-gray-200 rounded transition-colors"
                          title={isExpanded ? "Collapse" : "Expand"}
                        >
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-gray-600" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-gray-600" />
                          )}
                        </button>

                        <button
                          onClick={(e) => deleteTranslation(translation.id, e)}
                          className="p-1.5 hover:bg-red-100 rounded transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </button>
                      </div>
                    </div>

                    {/* Expanded view */}
                    {isExpanded && (
                      <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                        <div>
                          <p className="text-xs font-semibold text-gray-700 mb-1">
                            Original:
                          </p>
                          <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">
                            {translation.source_text}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs font-semibold text-gray-700 mb-1">
                            Translation:
                          </p>
                          <p className="text-sm text-gray-900 bg-blue-50 p-2 rounded">
                            {translation.translated_text}
                          </p>
                        </div>

                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <span>
                            Confidence: {Math.round(translation.confidence_score * 100)}%
                          </span>
                          <span>•</span>
                          <span>
                            {new Date(translation.created_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
