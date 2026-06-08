import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

const AccessibilityContext = createContext(null);

const STORAGE_KEY = "accessibility-prefs";

function loadPrefs() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
  } catch {
    return {};
  }
}

export function AccessibilityProvider({ children }) {
  const saved = loadPrefs();
  const [themeMode, setThemeMode] = useState(saved.themeMode || "light");
  const [fontScale, setFontScale] = useState(saved.fontScale || 1);
  const [colorBlind, setColorBlind] = useState(saved.colorBlind || false);
  const [ttsEnabled, setTtsEnabled] = useState(saved.ttsEnabled || false);

  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ themeMode, fontScale, colorBlind, ttsEnabled })
    );
  }, [themeMode, fontScale, colorBlind, ttsEnabled]);

  const speak = useCallback(
    (text) => {
      if (!("speechSynthesis" in window)) return;
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.rate = 1;
      window.speechSynthesis.speak(utter);
    },
    []
  );

  const speakIfEnabled = useCallback(
    (text) => {
      if (ttsEnabled) speak(text);
    },
    [ttsEnabled, speak]
  );

  const cycleTheme = useCallback(() => {
    setThemeMode((m) =>
      m === "light" ? "dark" : m === "dark" ? "highContrast" : "light"
    );
  }, []);

  const increaseFont = useCallback(
    () => setFontScale((f) => Math.min(2, +(f + 0.1).toFixed(2))),
    []
  );
  const decreaseFont = useCallback(
    () => setFontScale((f) => Math.max(0.8, +(f - 0.1).toFixed(2))),
    []
  );
  const resetFont = useCallback(() => setFontScale(1), []);

  const value = useMemo(
    () => ({
      themeMode,
      setThemeMode,
      cycleTheme,
      fontScale,
      increaseFont,
      decreaseFont,
      resetFont,
      colorBlind,
      setColorBlind,
      ttsEnabled,
      setTtsEnabled,
      speak,
      speakIfEnabled,
    }),
    [themeMode, fontScale, colorBlind, ttsEnabled, cycleTheme, increaseFont, decreaseFont, resetFont, speak, speakIfEnabled]
  );

  return (
    <AccessibilityContext.Provider value={value}>{children}</AccessibilityContext.Provider>
  );
}

export function useAccessibility() {
  return useContext(AccessibilityContext);
}
