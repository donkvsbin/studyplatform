import { describe, it, expect } from "vitest";
import { safeRedirect } from "../../src/utils/navigation";
import zh from "../../src/locales/zh-CN";
import en from "../../src/locales/en";
import { zhExtra, enExtra, zhErrors, enErrors } from "../../src/locales/extra";
function keys(value: Record<string, unknown>, prefix = ""): string[] {
  return Object.entries(value)
    .flatMap(([key, item]) =>
      typeof item === "object" && item !== null
        ? keys(item as Record<string, unknown>, prefix + key + ".")
        : [prefix + key],
    )
    .sort();
}
describe("navigation and translation contracts", () => {
  it("only returns safe local post-login destinations", () => {
    for (const value of [
      "https://evil.example",
      "//evil.example",
      "/\\evil.example",
      "/%2f%2fevil.example",
      "/%5cevil.example",
      "/\n/evil.example",
      "/login",
      "/register?redirect=/settings",
      null,
      ["/settings"],
    ])
      expect(safeRedirect(value)).toBe("/");
    expect(safeRedirect("/courses/1")).toBe("/courses/1");
    expect(safeRedirect("/assistant?course=1")).toBe("/assistant?course=1");
  });
  it("provides matching Chinese and English UI keys", () => {
    expect(keys(zh)).toEqual(keys(en));
    expect(keys(zhExtra)).toEqual(keys(enExtra));
    expect(keys(zhErrors)).toEqual(keys(enErrors));
  });
});
