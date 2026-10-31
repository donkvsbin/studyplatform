export type ThemePreference = "system" | "light" | "dark";
export type ColorTheme = "light" | "dark";

export function parseTheme(value: string | null): ThemePreference {
  return value === "light" || value === "dark" ? value : "system";
}

export function resolveTheme(
  preference: ThemePreference,
  systemDark: boolean,
): ColorTheme {
  return preference === "system" ? (systemDark ? "dark" : "light") : preference;
}
