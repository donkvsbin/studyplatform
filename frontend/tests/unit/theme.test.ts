import { describe, expect, it } from "vitest";
import { parseTheme, resolveTheme } from "../../src/utils/theme";

describe("theme preferences", () => {
  it("defaults missing or invalid preferences to the system", () => {
    for (const value of [null, "", "unknown", "system"])
      expect(parseTheme(value)).toBe("system");
    expect(parseTheme("light")).toBe("light");
    expect(parseTheme("dark")).toBe("dark");
  });
  it("resolves the system preference and respects a manual override", () => {
    expect(resolveTheme("system", true)).toBe("dark");
    expect(resolveTheme("system", false)).toBe("light");
    expect(resolveTheme("light", true)).toBe("light");
    expect(resolveTheme("dark", false)).toBe("dark");
  });
});
