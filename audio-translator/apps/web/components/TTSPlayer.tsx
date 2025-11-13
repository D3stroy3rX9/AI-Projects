"use client";

import { useState, useEffect, useCallback } from "react";
import { Volume2, VolumeX, Pause, Play } from "lucide-react";

interface TTSPlayerProps {
  text: string;
  language: string;
  autoPlay?: boolean;
}

export default function TTSPlayer({ text, language, autoPlay = false }: TTSPlayerProps) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [rate, setRate] = useState(1.0);
  const [pitch, setPitch] = useState(1.0);
  const [volume, setVolume] = useState(1.0);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>("");
  const [showControls, setShowControls] = useState(false);

  // Load available voices
  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);

      // Try to find a voice matching the language
      const languageVoice = availableVoices.find((voice) =>
        voice.lang.startsWith(language.split("-")[0])
      );
      if (languageVoice) {
        setSelectedVoice(languageVoice.name);
      }
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.cancel();
    };
  }, [language]);

  // Auto-play when text changes (if enabled)
  useEffect(() => {
    if (autoPlay && text && !isSpeaking) {
      handleSpeak();
    }
  }, [text, autoPlay]);

  const handleSpeak = useCallback(() => {
    if (!text) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    // Set language (convert ISO codes like 'es' to 'es-ES')
    const langCode = language.includes("-") ? language : `${language}-${language.toUpperCase()}`;
    utterance.lang = langCode;

    // Set voice if selected
    if (selectedVoice) {
      const voice = voices.find((v) => v.name === selectedVoice);
      if (voice) {
        utterance.voice = voice;
      }
    }

    // Set speech parameters
    utterance.rate = rate;
    utterance.pitch = pitch;
    utterance.volume = volume;

    // Event handlers
    utterance.onstart = () => {
      setIsSpeaking(true);
      setIsPaused(false);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setIsPaused(false);
    };

    utterance.onerror = (event) => {
      console.error("Speech synthesis error:", event);
      setIsSpeaking(false);
      setIsPaused(false);
    };

    window.speechSynthesis.speak(utterance);
  }, [text, language, selectedVoice, voices, rate, pitch, volume]);

  const handlePause = () => {
    if (isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
    } else {
      window.speechSynthesis.pause();
      setIsPaused(true);
    }
  };

  const handleStop = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsPaused(false);
  };

  if (!text) return null;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        {/* Main play/stop button */}
        {!isSpeaking ? (
          <button
            onClick={handleSpeak}
            className="p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors"
            title="Play text-to-speech"
          >
            <Volume2 className="w-5 h-5" />
          </button>
        ) : (
          <div className="flex gap-1">
            <button
              onClick={handlePause}
              className="p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors"
              title={isPaused ? "Resume" : "Pause"}
            >
              {isPaused ? <Play className="w-5 h-5" /> : <Pause className="w-5 h-5" />}
            </button>
            <button
              onClick={handleStop}
              className="p-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors"
              title="Stop"
            >
              <VolumeX className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Settings toggle */}
        <button
          onClick={() => setShowControls(!showControls)}
          className="text-sm text-gray-600 hover:text-gray-800 underline"
        >
          {showControls ? "Hide" : "Show"} Controls
        </button>

        {/* Speaking indicator */}
        {isSpeaking && !isPaused && (
          <div className="flex items-center gap-1 text-blue-600 text-sm">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
            Speaking...
          </div>
        )}
        {isPaused && (
          <div className="flex items-center gap-1 text-yellow-600 text-sm">
            <div className="w-2 h-2 bg-yellow-600 rounded-full"></div>
            Paused
          </div>
        )}
      </div>

      {/* Advanced controls */}
      {showControls && (
        <div className="bg-gray-50 p-4 rounded-lg space-y-3">
          {/* Speed control */}
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">
              Speed: {rate}x
            </label>
            <div className="flex gap-2 items-center">
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.25"
                value={rate}
                onChange={(e) => setRate(parseFloat(e.target.value))}
                className="flex-1"
              />
              <div className="flex gap-1">
                {[0.5, 1, 1.5, 2].map((speed) => (
                  <button
                    key={speed}
                    onClick={() => setRate(speed)}
                    className={`px-2 py-1 text-xs rounded ${
                      rate === speed
                        ? "bg-blue-500 text-white"
                        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                    }`}
                  >
                    {speed}x
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Volume control */}
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">
              Volume: {Math.round(volume * 100)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={(e) => setVolume(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Pitch control */}
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">
              Pitch: {pitch}
            </label>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={pitch}
              onChange={(e) => setPitch(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Voice selection */}
          {voices.length > 0 && (
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                Voice
              </label>
              <select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Default</option>
                {voices
                  .filter((voice) =>
                    voice.lang.startsWith(language.split("-")[0])
                  )
                  .map((voice) => (
                    <option key={voice.name} value={voice.name}>
                      {voice.name} ({voice.lang})
                    </option>
                  ))}
              </select>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
