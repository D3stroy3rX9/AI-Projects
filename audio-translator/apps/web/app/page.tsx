"use client";

import { useState } from "react";
import AudioRecorder from "@/components/AudioRecorder";
import TranslationDisplay from "@/components/TranslationDisplay";
import LanguageSelector from "@/components/LanguageSelector";
import TranslationHistory from "@/components/TranslationHistory";
import { useWebSocket } from "@/hooks/useWebSocket";
import Link from "next/link";

export default function Home() {
  // Language selection
  const [sourceLanguage, setSourceLanguage] = useState("auto");
  const [targetLanguage, setTargetLanguage] = useState("es");

  // Translation state
  const [transcription, setTranscription] = useState("");
  const [translation, setTranslation] = useState("");
  const [detectedLanguage, setDetectedLanguage] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [historyRefreshTrigger, setHistoryRefreshTrigger] = useState(0);

  // WebSocket connection
  const { sendAudio, isConnected, connectionStatus } = useWebSocket({
    onTranscription: (data) => {
      setTranscription(data.text);
      setDetectedLanguage(data.language);
      setConfidence(data.confidence);
    },
    onTranslation: (data) => {
      setTranslation(data.text);
      setIsProcessing(false);
      // Refresh history sidebar after translation is saved
      setHistoryRefreshTrigger((prev) => prev + 1);
    },
    onProcessing: () => {
      setIsProcessing(true);
    },
    onError: (error) => {
      console.error("WebSocket error:", error);
      setIsProcessing(false);
    },
  });

  const handleAudioRecorded = async (audioBase64: string) => {
    // Clear previous results
    setTranscription("");
    setTranslation("");
    setDetectedLanguage("");
    setIsProcessing(true);

    // Send audio to backend
    sendAudio({
      audioData: audioBase64,
      sourceLanguage,
      targetLanguage,
      sessionId: getSessionId(),
    });
  };

  const handleSwapLanguages = () => {
    if (sourceLanguage !== "auto") {
      setTargetLanguage(sourceLanguage);
    }
    setSourceLanguage(targetLanguage);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-between mb-4">
            <div className="flex-1"></div>
            <div className="flex-1 text-center">
              <h1 className="text-5xl font-bold text-gray-900 mb-3">
                🎤 Audio Auto-Translator
              </h1>
              <p className="text-lg text-gray-600">
                Speak in any language, get instant translation
              </p>
            </div>
            <div className="flex-1 flex justify-end">
              <Link
                href="/history"
                className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors text-sm font-medium"
              >
                View All History
              </Link>
            </div>
          </div>

          {/* Connection status */}
          <div className="mt-4">
            {isConnected ? (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                Connected
              </span>
            ) : (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                Disconnected
              </span>
            )}
          </div>
        </header>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Language Selectors */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                <LanguageSelector
                  label="From"
                  value={sourceLanguage}
                  onChange={setSourceLanguage}
                  includeAuto={true}
                />

                <div className="flex justify-center">
                  <button
                    onClick={handleSwapLanguages}
                    disabled={sourceLanguage === "auto"}
                    className="p-3 rounded-full hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Swap languages"
                  >
                    <svg
                      className="w-6 h-6 text-gray-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                      />
                    </svg>
                  </button>
                </div>

                <LanguageSelector
                  label="To"
                  value={targetLanguage}
                  onChange={setTargetLanguage}
                  includeAuto={false}
                />
              </div>
            </div>

            {/* Audio Recorder */}
            <div className="bg-white rounded-xl shadow-lg p-8">
              <AudioRecorder
                onAudioRecorded={handleAudioRecorded}
                isProcessing={isProcessing}
                isConnected={isConnected}
              />
            </div>

            {/* Translation Display */}
            {(transcription || translation || isProcessing) && (
              <TranslationDisplay
                transcription={transcription}
                translation={translation}
                sourceLanguage={detectedLanguage || sourceLanguage}
                targetLanguage={targetLanguage}
                confidence={confidence}
                isProcessing={isProcessing}
              />
            )}

            {/* Instructions */}
            {!transcription && !isProcessing && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">
                  How to use
                </h3>
                <ol className="text-blue-800 space-y-2 text-left max-w-md mx-auto">
                  <li>1. Select your source and target languages</li>
                  <li>2. Click the microphone button to start recording</li>
                  <li>3. Speak clearly in your chosen language</li>
                  <li>4. Click stop when finished</li>
                  <li>5. View your transcription and translation instantly!</li>
                </ol>
              </div>
            )}
          </div>

          {/* Right Column - History Sidebar */}
          <div className="lg:col-span-1">
            <div className="lg:sticky lg:top-8">
              <TranslationHistory
                sessionId={getSessionId()}
                refreshTrigger={historyRefreshTrigger}
                onTranslationSelect={(translation) => {
                  setTranscription(translation.source_text);
                  setTranslation(translation.translated_text);
                  setDetectedLanguage(translation.source_language);
                  setConfidence(translation.confidence_score);
                }}
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>
            Powered by Whisper (transcription) + LibreTranslate (translation)
          </p>
          <p className="mt-2">100% free • Privacy-focused • Real-time</p>
        </footer>
      </div>
    </main>
  );
}

// Helper function to get or create session ID
function getSessionId(): string {
  if (typeof window === "undefined") return "";

  let sessionId = sessionStorage.getItem("audio-translator-session");

  if (!sessionId) {
    sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem("audio-translator-session", sessionId);
  }

  return sessionId;
}
