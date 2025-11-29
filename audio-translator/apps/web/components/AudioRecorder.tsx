"use client";

import { useState, useRef, useEffect } from "react";

interface AudioRecorderProps {
  onAudioRecorded: (audioBase64: string) => void;
  isProcessing: boolean;
  isConnected: boolean;
}

export default function AudioRecorder({
  onAudioRecorded,
  isProcessing,
  isConnected,
}: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState("");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout>();
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number>();

  // Start recording
  const startRecording = async () => {
    try {
      setError("");

      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Set up audio level monitoring
      setupAudioLevelMonitoring(stream);

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = async () => {
        // Stop audio level monitoring
        stopAudioLevelMonitoring();

        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });

        // Convert to base64
        const base64Audio = await blobToBase64(audioBlob);

        // Send to parent component
        onAudioRecorded(base64Audio);

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());

        // Reset
        audioChunksRef.current = [];
      };

      // Start recording
      mediaRecorder.start();
      setIsRecording(true);

      // Start timer
      setRecordingTime(0);
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      console.error("Failed to start recording:", err);

      if (err instanceof Error) {
        if (err.name === "NotAllowedError") {
          setError(
            "Microphone permission denied. Please allow microphone access."
          );
        } else if (err.name === "NotFoundError") {
          setError("No microphone found. Please connect a microphone.");
        } else {
          setError("Failed to start recording. Please try again.");
        }
      }
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      // Stop timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }

      setRecordingTime(0);
    }
  };

  // Set up audio level monitoring
  const setupAudioLevelMonitoring = (stream: MediaStream) => {
    try {
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);

      analyser.fftSize = 256;
      microphone.connect(analyser);

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      // Start monitoring
      monitorAudioLevel();
    } catch (err) {
      console.error("Failed to set up audio monitoring:", err);
    }
  };

  // Monitor audio level
  const monitorAudioLevel = () => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

    const updateLevel = () => {
      if (!analyserRef.current) return;

      analyserRef.current.getByteFrequencyData(dataArray);

      // Calculate average volume
      const average =
        dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;

      // Normalize to 0-100
      const normalizedLevel = Math.min(100, (average / 255) * 200);

      setAudioLevel(normalizedLevel);

      animationRef.current = requestAnimationFrame(updateLevel);
    };

    updateLevel();
  };

  // Stop audio level monitoring
  const stopAudioLevelMonitoring = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
    }

    setAudioLevel(0);
  };

  // Convert blob to base64
  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onloadend = () => {
        if (typeof reader.result === "string") {
          // Remove data URL prefix (data:audio/webm;base64,)
          const base64 = reader.result.split(",")[1];
          resolve(base64);
        } else {
          reject(new Error("Failed to convert blob to base64"));
        }
      };

      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  // Format time as MM:SS
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      stopAudioLevelMonitoring();
    };
  }, []);

  return (
    <div className="flex flex-col items-center">
      {/* Error message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm w-full">
          {error}
        </div>
      )}

      {/* Record button */}
      <div className="relative mb-6">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing || !isConnected}
          className={`
            relative w-24 h-24 rounded-full flex items-center justify-center
            transition-all duration-300 shadow-lg
            ${
              isRecording
                ? "bg-red-500 hover:bg-red-600 animate-pulse"
                : "bg-blue-500 hover:bg-blue-600"
            }
            disabled:opacity-50 disabled:cursor-not-allowed
            focus:outline-none focus:ring-4 focus:ring-blue-300
          `}
          title={isRecording ? "Stop recording" : "Start recording"}
        >
          {isRecording ? (
            // Stop icon
            <svg
              className="w-10 h-10 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          ) : (
            // Microphone icon
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
          )}

          {/* Pulsing ring when recording */}
          {isRecording && (
            <span className="absolute inset-0 rounded-full bg-red-400 opacity-75 animate-ping"></span>
          )}
        </button>
      </div>

      {/* Status text */}
      <p className="text-gray-700 font-medium mb-2">
        {isRecording
          ? "Recording..."
          : isProcessing
          ? "Processing..."
          : "Click to start recording"}
      </p>

      {/* Recording timer */}
      {isRecording && (
        <p className="text-2xl font-mono text-gray-800 mb-4">
          {formatTime(recordingTime)}
        </p>
      )}

      {/* Audio level meter */}
      {isRecording && (
        <div className="w-64 mb-4">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all duration-100"
              style={{ width: `${audioLevel}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 text-center mt-1">Audio Level</p>
        </div>
      )}

      {/* Processing indicator */}
      {isProcessing && (
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
          <span className="text-sm">Transcribing & translating...</span>
        </div>
      )}

      {/* Connection warning */}
      {!isConnected && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm">
          ⚠️ Not connected to server. Please wait...
        </div>
      )}
    </div>
  );
}
