export function safeRedirect(value: unknown): string {
  if (typeof value !== "string") return "/";
  let decoded: string;
  try {
    decoded = decodeURIComponent(value);
  } catch {
    return "/";
  }
  if (
    !decoded.startsWith("/") ||
    decoded.startsWith("//") ||
    /[\\\u0000-\u001f]/.test(decoded) ||
    /^\/(login|register)([/?#]|$)/.test(decoded)
  )
    return "/";
  return value;
}
