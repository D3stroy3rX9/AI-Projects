"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import AudioRecorder from "@/components/AudioRecorder";
import LanguageSelector from "@/components/LanguageSelector";
import ConversationView, {
  ConversationMessage,
} from "@/components/ConversationView";
import { useWebSocket } from "@/hooks/useWebSocket";
import { ArrowLeft } from "lucide-react";

export default function ConversationPage() {
  // Current speaker
  const [currentSpeaker, setCurrentSpeaker] = useState<"A" | "B">("A");

  // Languages for each person
  const [personALanguage, setPersonALanguage] = useState("en");
  const [personBLanguage, setPersonBLanguage] = useState("es");

  // Conversation messages
  const [messages, setMessages] = useState<ConversationMessage[]>([]);

  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTranscription, setCurrentTranscription] = useState("");
  const [currentTranslation, setCurrentTranslation] = useState("");

  // Get session ID
  const getSessionId = () => {
    if (typeof window === "undefined") return "";
    let sessionId = sessionStorage.getItem("audio-translator-conversation");
    if (!sessionId) {
      sessionId = `conversation-${Date.now()}-${Math.random()
        .toString(36)
        .substr(2, 9)}`;
      sessionStorage.setItem("audio-translator-conversation", sessionId);
    }
    return sessionId;
  };

  // WebSocket connection
  const { sendAudio, isConnected } = useWebSocket({
    onTranscription: (data) => {
      setCurrentTranscription(data.text);
    },
    onTranslation: (data) => {
      setCurrentTranslation(data.text);

      // Get languages based on current speaker
      const sourceLanguage =
        currentSpeaker === "A" ? personALanguage : personBLanguage;
      const targetLanguage =
        currentSpeaker === "A" ? personBLanguage : personALanguage;

      // Add message to conversation
      const newMessage: ConversationMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        speaker: currentSpeaker,
        sourceText: currentTranscription,
        translatedText: data.text,
        sourceLanguage: data.source || sourceLanguage,
        targetLanguage: data.target || targetLanguage,
        timestamp: new Date(),
        confidence: 0.95, // Will be updated with actual confidence from transcription
      };

      setMessages((prev) => [...prev, newMessage]);

      // Switch to other speaker
      setCurrentSpeaker((prev) => (prev === "A" ? "B" : "A"));

      // Clear current state
      setCurrentTranscription("");
      setCurrentTranslation("");
      setIsProcessing(false);
    },
    onProcessing: () => {
      setIsProcessing(true);
    },
    onError: (error) => {
      console.error("WebSocket error:", error);
      setIsProcessing(false);
    },
  });

  const handleAudioRecorded = useCallback(
    (audioBase64: string) => {
      setIsProcessing(true);
      setCurrentTranscription("");
      setCurrentTranslation("");

      const sourceLanguage =
        currentSpeaker === "A" ? personALanguage : personBLanguage;
      const targetLanguage =
        currentSpeaker === "A" ? personBLanguage : personALanguage;

      sendAudio({
        audioData: audioBase64,
        sourceLanguage,
        targetLanguage,
        sessionId: getSessionId(),
      });
    },
    [currentSpeaker, personALanguage, personBLanguage, sendAudio]
  );

  const handleClearConversation = () => {
    if (
      confirm(
        "Are you sure you want to clear the entire conversation? This cannot be undone."
      )
    ) {
      setMessages([]);
      setCurrentSpeaker("A");
    }
  };

  const handleExportConversation = () => {
    const content = messages
      .map((msg) => {
        const time = msg.timestamp.toLocaleString();
        const speaker = `Person ${msg.speaker}`;
        return `[${time}] ${speaker}\nOriginal: ${msg.sourceText}\nTranslation: ${msg.translatedText}\n`;
      })
      .join("\n---\n\n");

    const dataUri = `data:text/plain;charset=utf-8,${encodeURIComponent(
      content
    )}`;
    const exportFileDefaultName = `conversation-${new Date().toISOString()}.txt`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8 h-screen flex flex-col">
        {/* Header */}
        <header className="mb-6">
          <div className="flex items-center justify-between">
            <Link
              href="/"
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors shadow"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Translator
            </Link>

            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                💬 Conversation Mode
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Two-way real-time translation
              </p>
            </div>

            <div>
              {isConnected ? (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                  Connected
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100">
                  <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                  Disconnected
                </span>
              )}
            </div>
          </div>
        </header>

        {/* Main Content - Split Screen */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 overflow-hidden">
          {/* Left Side - Person A */}
          <div className="flex flex-col bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
            {/* Person A Header */}
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
              <h2 className="text-white text-xl font-semibold flex items-center gap-2">
                <span
                  className={`w-3 h-3 rounded-full ${
                    currentSpeaker === "A"
                      ? "bg-green-400 animate-pulse"
                      : "bg-white/50"
                  }`}
                ></span>
                Person A
              </h2>
              <p className="text-white/80 text-sm mt-1">
                {currentSpeaker === "A" ? "Your turn to speak" : "Listening..."}
              </p>
            </div>

            {/* Language Selector */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <LanguageSelector
                label="Person A speaks"
                value={personALanguage}
                onChange={setPersonALanguage}
                includeAuto={false}
              />
            </div>

            {/* Audio Recorder for Person A */}
            <div className="p-6">
              <AudioRecorder
                onAudioRecorded={handleAudioRecorded}
                isProcessing={isProcessing && currentSpeaker === "A"}
                isConnected={isConnected}
                disabled={currentSpeaker !== "A" || isProcessing}
              />

              {currentSpeaker !== "A" && !isProcessing && (
                <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-4">
                  Wait for Person B to finish
                </p>
              )}
            </div>
          </div>

          {/* Right Side - Person B */}
          <div className="flex flex-col bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
            {/* Person B Header */}
            <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4">
              <h2 className="text-white text-xl font-semibold flex items-center gap-2">
                <span
                  className={`w-3 h-3 rounded-full ${
                    currentSpeaker === "B"
                      ? "bg-green-400 animate-pulse"
                      : "bg-white/50"
                  }`}
                ></span>
                Person B
              </h2>
              <p className="text-white/80 text-sm mt-1">
                {currentSpeaker === "B" ? "Your turn to speak" : "Listening..."}
              </p>
            </div>

            {/* Language Selector */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <LanguageSelector
                label="Person B speaks"
                value={personBLanguage}
                onChange={setPersonBLanguage}
                includeAuto={false}
              />
            </div>

            {/* Audio Recorder for Person B */}
            <div className="p-6">
              <AudioRecorder
                onAudioRecorded={handleAudioRecorded}
                isProcessing={isProcessing && currentSpeaker === "B"}
                isConnected={isConnected}
                disabled={currentSpeaker !== "B" || isProcessing}
              />

              {currentSpeaker !== "B" && !isProcessing && (
                <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-4">
                  Wait for Person A to finish
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Conversation History */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden h-96">
          <ConversationView
            messages={messages}
            onClearConversation={handleClearConversation}
            onExportConversation={handleExportConversation}
            personALanguage={personALanguage}
            personBLanguage={personBLanguage}
          />
        </div>
      </div>
    </div>
  );
}
