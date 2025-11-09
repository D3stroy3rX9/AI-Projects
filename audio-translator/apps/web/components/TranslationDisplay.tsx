"use client";

import { useState } from "react";

interface TranslationDisplayProps {
  transcription: string;
  translation: string;
  sourceLanguage: string;
  targetLanguage: string;
  confidence: number;
  isProcessing: boolean;
}

// Language names map
const LANGUAGE_NAMES: { [key: string]: string } = {
  auto: "Auto",
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

export default function TranslationDisplay({
  transcription,
  translation,
  sourceLanguage,
  targetLanguage,
  confidence,
  isProcessing,
}: TranslationDisplayProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  // Copy text to clipboard
  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);

      // Reset after 2 seconds
      setTimeout(() => {
        setCopiedField(null);
      }, 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  const getLanguageName = (code: string): string => {
    return LANGUAGE_NAMES[code] || code.toUpperCase();
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-500 px-6 py-4">
        <h2 className="text-white text-xl font-semibold">Results</h2>
      </div>

      <div className="p-6">
        {/* Two-column layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Original transcription */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 flex items-center">
                <span className="text-2xl mr-2">🎤</span>
                Original ({getLanguageName(sourceLanguage)})
              </h3>

              {transcription && (
                <button
                  onClick={() => copyToClipboard(transcription, "transcription")}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Copy transcription"
                >
                  {copiedField === "transcription" ? (
                    <svg
                      className="w-5 h-5 text-green-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="w-5 h-5 text-gray-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                      />
                    </svg>
                  )}
                </button>
              )}
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 min-h-[120px]">
              {isProcessing && !transcription ? (
                <div className="flex items-center justify-center h-full">
                  <div className="flex items-center space-x-2 text-gray-500">
                    <svg
                      className="animate-spin h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    <span className="text-sm">Transcribing...</span>
                  </div>
                </div>
              ) : transcription ? (
                <p className="text-gray-900 text-lg leading-relaxed">
                  {transcription}
                </p>
              ) : (
                <p className="text-gray-400 text-sm italic">
                  Transcription will appear here...
                </p>
              )}
            </div>

            {/* Confidence score */}
            {confidence > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Confidence:</span>
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      confidence > 0.8
                        ? "bg-green-500"
                        : confidence > 0.6
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                    style={{ width: `${confidence * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {Math.round(confidence * 100)}%
                </span>
              </div>
            )}
          </div>

          {/* Translation */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 flex items-center">
                <span className="text-2xl mr-2">🌍</span>
                Translation ({getLanguageName(targetLanguage)})
              </h3>

              {translation && !translation.startsWith("[") && (
                <button
                  onClick={() => copyToClipboard(translation, "translation")}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Copy translation"
                >
                  {copiedField === "translation" ? (
                    <svg
                      className="w-5 h-5 text-green-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="w-5 h-5 text-gray-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                      />
                    </svg>
                  )}
                </button>
              )}
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 min-h-[120px]">
              {isProcessing && !translation ? (
                <div className="flex items-center justify-center h-full">
                  <div className="flex items-center space-x-2 text-blue-600">
                    <svg
                      className="animate-spin h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    <span className="text-sm">Translating...</span>
                  </div>
                </div>
              ) : translation ? (
                <p className="text-gray-900 text-lg font-medium leading-relaxed">
                  {translation}
                </p>
              ) : (
                <p className="text-gray-400 text-sm italic">
                  Translation will appear here...
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Success animation */}
        {transcription && translation && !isProcessing && (
          <div className="mt-6 flex items-center justify-center">
            <div className="flex items-center space-x-2 text-green-600 bg-green-50 px-4 py-2 rounded-full">
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-sm font-medium">
                Translation complete!
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
