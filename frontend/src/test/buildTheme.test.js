import { describe, expect, it } from "vitest";
import { buildTheme, chartColors, COLORBLIND_PALETTE } from "../theme/buildTheme";

describe("buildTheme", () => {
  it("creates a light theme by default", () => {
    const theme = buildTheme("light", 1);
    expect(theme.palette.mode).toBe("light");
  });

  it("creates a dark theme", () => {
    const theme = buildTheme("dark", 1);
    expect(theme.palette.mode).toBe("dark");
  });

  it("applies high contrast colors", () => {
    const theme = buildTheme("highContrast", 1);
    expect(theme.palette.mode).toBe("dark");
    expect(theme.palette.background.default).toBe("#000000");
    expect(theme.palette.primary.main).toBe("#ffff00");
  });

  it("scales font size", () => {
    const theme = buildTheme("light", 1.5);
    expect(theme.typography.fontSize).toBeCloseTo(21);
  });
});

describe("chartColors", () => {
  it("returns color-blind palette when enabled", () => {
    expect(chartColors(true)).toEqual(COLORBLIND_PALETTE);
  });

  it("returns default palette when disabled", () => {
    expect(chartColors(false)).not.toEqual(COLORBLIND_PALETTE);
  });
});
