import { describe, expect, it } from "vitest";
import { resolveTheme } from "../../src/utils/theme";

describe("theme preferences", () => {
  it("uses the current system appearance", () => {
    expect(resolveTheme("system", true)).toBe("dark");
    expect(resolveTheme("system", false)).toBe("light");
  });
  it("keeps the current manual choice when the system changes", () => {
    expect(resolveTheme("light", true)).toBe("light");
    expect(resolveTheme("light", false)).toBe("light");
    expect(resolveTheme("dark", true)).toBe("dark");
    expect(resolveTheme("dark", false)).toBe("dark");
  });
});
