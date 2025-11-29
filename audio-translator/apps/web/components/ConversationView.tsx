"use client";

import { useState, useEffect, useRef } from "react";
import { Trash2, Download, Volume2 } from "lucide-react";
import TTSPlayer from "./TTSPlayer";

export interface ConversationMessage {
  id: string;
  speaker: "A" | "B";
  sourceText: string;
  translatedText: string;
  sourceLanguage: string;
  targetLanguage: string;
  timestamp: Date;
  confidence: number;
}

interface ConversationViewProps {
  messages: ConversationMessage[];
  onClearConversation: () => void;
  onExportConversation: () => void;
  personALanguage: string;
  personBLanguage: string;
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

export default function ConversationView({
  messages,
  onClearConversation,
  onExportConversation,
  personALanguage,
  personBLanguage,
}: ConversationViewProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showTTSControls, setShowTTSControls] = useState<string | null>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const getLanguageName = (code: string): string => {
    return LANGUAGE_NAMES[code] || code.toUpperCase();
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-500 px-6 py-4 flex items-center justify-between">
        <div className="text-white">
          <h2 className="text-xl font-semibold">Conversation Mode</h2>
          <p className="text-sm text-white/80">
            {messages.length} {messages.length === 1 ? "message" : "messages"}
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={onExportConversation}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors flex items-center gap-2"
            title="Export conversation"
          >
            <Download className="w-4 h-4" />
            Export
          </button>

          <button
            onClick={onClearConversation}
            className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex items-center gap-2"
            title="Clear conversation"
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <p className="text-lg font-medium">No messages yet</p>
              <p className="text-sm mt-2">
                Start recording to begin the conversation
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.speaker === "A" ? "justify-start" : "justify-end"
                } animate-fade-in`}
              >
                <div
                  className={`max-w-[70%] rounded-lg shadow-md ${
                    message.speaker === "A"
                      ? "bg-blue-100 dark:bg-blue-900"
                      : "bg-green-100 dark:bg-green-900"
                  }`}
                >
                  {/* Message header */}
                  <div
                    className={`px-4 py-2 border-b ${
                      message.speaker === "A"
                        ? "border-blue-200 dark:border-blue-800"
                        : "border-green-200 dark:border-green-800"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className={`text-sm font-semibold ${
                          message.speaker === "A"
                            ? "text-blue-900 dark:text-blue-100"
                            : "text-green-900 dark:text-green-100"
                        }`}
                      >
                        Person {message.speaker}
                      </span>
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        {formatTime(message.timestamp)}
                      </span>
                    </div>
                  </div>

                  {/* Original text */}
                  <div className="px-4 py-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                        Original ({getLanguageName(message.sourceLanguage)})
                      </span>
                      <button
                        onClick={() =>
                          setShowTTSControls(
                            showTTSControls === `${message.id}-source`
                              ? null
                              : `${message.id}-source`
                          )
                        }
                        className="p-1 hover:bg-black/10 rounded transition-colors"
                        title="Text-to-speech"
                      >
                        <Volume2 className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                      </button>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                      {message.sourceText}
                    </p>

                    {showTTSControls === `${message.id}-source` && (
                      <div className="mt-2 pt-2 border-t border-black/10">
                        <TTSPlayer
                          text={message.sourceText}
                          language={message.sourceLanguage}
                          autoPlay={false}
                        />
                      </div>
                    )}
                  </div>

                  {/* Translation */}
                  <div
                    className={`px-4 py-3 border-t ${
                      message.speaker === "A"
                        ? "border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950"
                        : "border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                        Translation ({getLanguageName(message.targetLanguage)})
                      </span>
                      <button
                        onClick={() =>
                          setShowTTSControls(
                            showTTSControls === `${message.id}-translation`
                              ? null
                              : `${message.id}-translation`
                          )
                        }
                        className="p-1 hover:bg-black/10 rounded transition-colors"
                        title="Text-to-speech"
                      >
                        <Volume2 className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                      </button>
                    </div>
                    <p
                      className={`text-base font-medium ${
                        message.speaker === "A"
                          ? "text-blue-900 dark:text-blue-100"
                          : "text-green-900 dark:text-green-100"
                      }`}
                    >
                      {message.translatedText}
                    </p>

                    {showTTSControls === `${message.id}-translation` && (
                      <div className="mt-2 pt-2 border-t border-black/10">
                        <TTSPlayer
                          text={message.translatedText}
                          language={message.targetLanguage}
                          autoPlay={false}
                        />
                      </div>
                    )}
                  </div>

                  {/* Confidence indicator */}
                  {message.confidence > 0 && (
                    <div className="px-4 py-2">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              message.confidence > 0.8
                                ? "bg-green-500"
                                : message.confidence > 0.6
                                ? "bg-yellow-500"
                                : "bg-red-500"
                            }`}
                            style={{ width: `${message.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {Math.round(message.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
    </div>
  );
}
