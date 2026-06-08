import { createTheme } from "@mui/material/styles";

// Color-blind-friendly categorical palette (Okabe-Ito) used for charts.
export const COLORBLIND_PALETTE = [
  "#0072B2",
  "#E69F00",
  "#009E73",
  "#D55E00",
  "#CC79A7",
  "#56B4E9",
  "#F0E442",
];

export const DEFAULT_PALETTE = [
  "#1976d2",
  "#9c27b0",
  "#2e7d32",
  "#ed6c02",
  "#d32f2f",
  "#0288d1",
  "#7b1fa2",
];

export function chartColors(colorBlind) {
  return colorBlind ? COLORBLIND_PALETTE : DEFAULT_PALETTE;
}

/**
 * Build a MUI theme from accessibility preferences.
 * @param {"light"|"dark"|"highContrast"} mode
 * @param {number} fontScale  multiplier, e.g. 1.0, 1.25
 */
export function buildTheme(mode, fontScale = 1) {
  const isHighContrast = mode === "highContrast";
  const paletteMode = mode === "dark" || isHighContrast ? "dark" : "light";

  const base = {
    palette: {
      mode: paletteMode,
      ...(isHighContrast
        ? {
            background: { default: "#000000", paper: "#000000" },
            text: { primary: "#ffffff", secondary: "#ffff00" },
            primary: { main: "#ffff00" },
            secondary: { main: "#00ffff" },
            divider: "#ffffff",
          }
        : {}),
    },
    typography: {
      fontSize: 14 * fontScale,
      htmlFontSize: 16,
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          "*:focus-visible": {
            outline: isHighContrast ? "3px solid #ffff00" : "3px solid #1976d2",
            outlineOffset: "2px",
          },
          a: { color: isHighContrast ? "#00ffff" : undefined },
        },
      },
      MuiButton: {
        defaultProps: { disableElevation: true },
        styleOverrides: {
          root: isHighContrast
            ? { border: "1px solid #ffffff", color: "#ffff00" }
            : {},
        },
      },
    },
  };

  return createTheme(base);
}
