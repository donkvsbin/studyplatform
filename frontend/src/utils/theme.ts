export type ThemePreference = "system" | "light" | "dark";
export type ColorTheme = "light" | "dark";

export function resolveTheme(
  preference: ThemePreference,
  systemDark: boolean,
): ColorTheme {
  return preference === "system" ? (systemDark ? "dark" : "light") : preference;
}
