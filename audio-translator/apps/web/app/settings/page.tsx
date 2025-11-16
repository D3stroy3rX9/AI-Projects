"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, Save } from "lucide-react";
import { useTheme } from "@/components/ThemeProvider";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();

  // User preferences
  const [defaultSourceLanguage, setDefaultSourceLanguage] = useState("auto");
  const [defaultTargetLanguage, setDefaultTargetLanguage] = useState("es");
  const [autoDetectLanguage, setAutoDetectLanguage] = useState(true);
  const [autoPlayTTS, setAutoPlayTTS] = useState(false);
  const [ttsSpeed, setTtsSpeed] = useState(1.0);
  const [audioQuality, setAudioQuality] = useState(16000);
  const [saveHistory, setSaveHistory] = useState(true);
  const [autoDeleteDays, setAutoDeleteDays] = useState(30);

  // Load settings from localStorage
  useEffect(() => {
    const loadSettings = () => {
      const settings = localStorage.getItem("app-settings");
      if (settings) {
        try {
          const parsed = JSON.parse(settings);
          setDefaultSourceLanguage(parsed.defaultSourceLanguage || "auto");
          setDefaultTargetLanguage(parsed.defaultTargetLanguage || "es");
          setAutoDetectLanguage(parsed.autoDetectLanguage ?? true);
          setAutoPlayTTS(parsed.autoPlayTTS ?? false);
          setTtsSpeed(parsed.ttsSpeed || 1.0);
          setAudioQuality(parsed.audioQuality || 16000);
          setSaveHistory(parsed.saveHistory ?? true);
          setAutoDeleteDays(parsed.autoDeleteDays || 30);
        } catch (error) {
          console.error("Error loading settings:", error);
        }
      }
    };

    loadSettings();
  }, []);

  // Save settings to localStorage
  const handleSaveSettings = () => {
    const settings = {
      defaultSourceLanguage,
      defaultTargetLanguage,
      autoDetectLanguage,
      autoPlayTTS,
      ttsSpeed,
      audioQuality,
      saveHistory,
      autoDeleteDays,
    };

    localStorage.setItem("app-settings", JSON.stringify(settings));
    alert("Settings saved successfully!");
  };

  // Clear cache
  const handleClearCache = () => {
    if (confirm("Are you sure you want to clear all cache? This cannot be undone.")) {
      // Clear all localStorage except theme
      const themeValue = localStorage.getItem("theme");
      localStorage.clear();
      if (themeValue) {
        localStorage.setItem("theme", themeValue);
      }
      alert("Cache cleared successfully!");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <Link
              href="/"
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors shadow"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Translator
            </Link>

            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              ⚙️ Settings
            </h1>

            <button
              onClick={handleSaveSettings}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors shadow"
            >
              <Save className="w-4 h-4" />
              Save Settings
            </button>
          </div>
        </header>

        {/* Settings Sections */}
        <div className="space-y-6">
          {/* Language Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Language Preferences
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Default Source Language
                </label>
                <select
                  value={defaultSourceLanguage}
                  onChange={(e) => setDefaultSourceLanguage(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="auto">Auto-detect</option>
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="zh">Chinese</option>
                  <option value="ja">Japanese</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Default Target Language
                </label>
                <select
                  value={defaultTargetLanguage}
                  onChange={(e) => setDefaultTargetLanguage(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="zh">Chinese</option>
                  <option value="ja">Japanese</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="auto-detect"
                  checked={autoDetectLanguage}
                  onChange={(e) => setAutoDetectLanguage(e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                />
                <label
                  htmlFor="auto-detect"
                  className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  Enable auto-detect for source language
                </label>
              </div>
            </div>
          </div>

          {/* Text-to-Speech Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Text-to-Speech
            </h2>

            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="auto-play-tts"
                  checked={autoPlayTTS}
                  onChange={(e) => setAutoPlayTTS(e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                />
                <label
                  htmlFor="auto-play-tts"
                  className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  Auto-play translations (automatically speak translated text)
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Default TTS Speed: {ttsSpeed}x
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.25"
                  value={ttsSpeed}
                  onChange={(e) => setTtsSpeed(parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>0.5x</span>
                  <span>1x</span>
                  <span>1.5x</span>
                  <span>2x</span>
                </div>
              </div>
            </div>
          </div>

          {/* Theme Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Appearance
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Theme
                </label>
                <div className="grid grid-cols-3 gap-4">
                  <button
                    onClick={() => setTheme("light")}
                    className={`px-4 py-3 rounded-lg border-2 transition-colors ${
                      theme === "light"
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-900 text-blue-900 dark:text-blue-100"
                        : "border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                    }`}
                  >
                    ☀️ Light
                  </button>
                  <button
                    onClick={() => setTheme("dark")}
                    className={`px-4 py-3 rounded-lg border-2 transition-colors ${
                      theme === "dark"
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-900 text-blue-900 dark:text-blue-100"
                        : "border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                    }`}
                  >
                    🌙 Dark
                  </button>
                  <button
                    onClick={() => setTheme("system")}
                    className={`px-4 py-3 rounded-lg border-2 transition-colors ${
                      theme === "system"
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-900 text-blue-900 dark:text-blue-100"
                        : "border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                    }`}
                  >
                    💻 System
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Audio Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Audio Quality
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Sample Rate
                </label>
                <select
                  value={audioQuality}
                  onChange={(e) => setAudioQuality(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value={8000}>8 kHz (Low quality, faster)</option>
                  <option value={16000}>16 kHz (Recommended)</option>
                  <option value={44100}>44.1 kHz (High quality, slower)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Privacy Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Privacy & Storage
            </h2>

            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="save-history"
                  checked={saveHistory}
                  onChange={(e) => setSaveHistory(e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                />
                <label
                  htmlFor="save-history"
                  className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  Save translation history
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Auto-delete history after (days)
                </label>
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={autoDeleteDays}
                  onChange={(e) => setAutoDeleteDays(Number(e.target.value))}
                  disabled={!saveHistory}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>

              <button
                onClick={handleClearCache}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                Clear All Cache
              </button>
            </div>
          </div>

          {/* Keyboard Shortcuts Info */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Keyboard Shortcuts
            </h2>

            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <div className="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                <span>Start/Stop Recording</span>
                <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded">
                  Space
                </kbd>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                <span>Play TTS</span>
                <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded">
                  Ctrl + Enter
                </kbd>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                <span>Copy Translation</span>
                <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded">
                  Ctrl + C
                </kbd>
              </div>
              <div className="flex items-center justify-between py-2">
                <span>Toggle Dark Mode</span>
                <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded">
                  Ctrl + Shift + D
                </kbd>
              </div>
            </div>
          </div>

          {/* About */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              About
            </h2>

            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <p>
                <strong>Version:</strong> 0.3.0
              </p>
              <p>
                <strong>Tech Stack:</strong> Next.js 14, FastAPI, Whisper,
                LibreTranslate
              </p>
              <p>
                <strong>License:</strong> MIT (Code) + Model Licenses
              </p>
              <p className="pt-4 text-xs text-gray-500 dark:text-gray-400">
                Powered by OpenAI Whisper (transcription) and LibreTranslate
                (translation). 100% free and privacy-focused. All processing
                happens locally or through free APIs.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
