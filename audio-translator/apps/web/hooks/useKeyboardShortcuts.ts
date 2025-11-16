import { useEffect } from "react";

interface KeyboardShortcuts {
  onSpace?: () => void;
  onCtrlEnter?: () => void;
  onCtrlC?: () => void;
  onCtrlShiftD?: () => void;
  onEscape?: () => void;
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcuts) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore shortcuts when typing in input fields
      const target = event.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      ) {
        return;
      }

      // Space - Start/Stop recording
      if (event.code === "Space" && shortcuts.onSpace) {
        event.preventDefault();
        shortcuts.onSpace();
      }

      // Ctrl + Enter - Play TTS
      if (event.ctrlKey && event.key === "Enter" && shortcuts.onCtrlEnter) {
        event.preventDefault();
        shortcuts.onCtrlEnter();
      }

      // Ctrl + C - Copy translation (only if handler is provided)
      if (event.ctrlKey && event.key === "c" && shortcuts.onCtrlC) {
        event.preventDefault();
        shortcuts.onCtrlC();
      }

      // Ctrl + Shift + D - Toggle dark mode
      if (
        event.ctrlKey &&
        event.shiftKey &&
        event.key === "D" &&
        shortcuts.onCtrlShiftD
      ) {
        event.preventDefault();
        shortcuts.onCtrlShiftD();
      }

      // Escape - Clear/cancel
      if (event.key === "Escape" && shortcuts.onEscape) {
        event.preventDefault();
        shortcuts.onEscape();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [shortcuts]);
}
