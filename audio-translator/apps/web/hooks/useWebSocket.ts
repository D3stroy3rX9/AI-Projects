import { useEffect, useRef, useState, useCallback } from "react";

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface UseWebSocketOptions {
  onTranscription?: (data: any) => void;
  onTranslation?: (data: any) => void;
  onProcessing?: () => void;
  onError?: (error: string) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
}

interface SendAudioParams {
  audioData: string;
  sourceLanguage: string;
  targetLanguage: string;
  sessionId: string;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState("disconnected");
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);

  // WebSocket URL (from environment or default)
  const WS_URL =
    process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/translate";

  const connect = useCallback(() => {
    try {
      console.log("Connecting to WebSocket:", WS_URL);

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebSocket connected");
        setIsConnected(true);
        setConnectionStatus("connected");
        reconnectAttemptsRef.current = 0;
        options.onConnected?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log("WebSocket message:", message);

          switch (message.type) {
            case "connected":
              console.log("Server confirmed connection:", message.message);
              break;

            case "processing":
              options.onProcessing?.();
              break;

            case "transcription":
              options.onTranscription?.(message);
              break;

            case "translation":
              options.onTranslation?.(message);
              break;

            case "error":
              console.error("Server error:", message.message);
              options.onError?.(message.message);
              break;

            case "warning":
              console.warn("Server warning:", message.message);
              options.onError?.(message.message);
              break;

            case "saved":
              console.log("Translation saved:", message.translation_id);
              break;

            case "pong":
              // Heartbeat response
              break;

            default:
              console.log("Unknown message type:", message.type);
          }
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setConnectionStatus("error");
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setIsConnected(false);
        setConnectionStatus("disconnected");
        options.onDisconnected?.();

        // Attempt to reconnect with exponential backoff
        const maxAttempts = 5;
        const baseDelay = 1000; // 1 second

        if (reconnectAttemptsRef.current < maxAttempts) {
          const delay = baseDelay * Math.pow(2, reconnectAttemptsRef.current);
          console.log(
            `Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        } else {
          console.error("Max reconnection attempts reached");
          setConnectionStatus("failed");
        }
      };
    } catch (error) {
      console.error("Failed to create WebSocket:", error);
      setConnectionStatus("error");
    }
  }, [WS_URL, options]);

  // Connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  // Send audio data to server
  const sendAudio = useCallback(
    (params: SendAudioParams) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not connected");
        options.onError?.("WebSocket is not connected. Please wait...");
        return;
      }

      const message = {
        type: "audio_chunk",
        data: params.audioData,
        source_lang: params.sourceLanguage,
        target_lang: params.targetLanguage,
        session_id: params.sessionId,
      };

      try {
        wsRef.current.send(JSON.stringify(message));
        console.log("Audio sent to server");
      } catch (error) {
        console.error("Failed to send audio:", error);
        options.onError?.("Failed to send audio");
      }
    },
    [options]
  );

  // Send ping to keep connection alive
  const sendPing = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "ping" }));
    }
  }, []);

  // Manual reconnect
  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  return {
    isConnected,
    connectionStatus,
    sendAudio,
    sendPing,
    reconnect,
  };
}
