import { i18n } from "../locales";
export class ApiError extends Error {
  constructor(
    public code: string,
    public status = 0,
    public fields?: Record<string, string>,
  ) {
    super(code);
  }
}
let token: string | null = null;
export function resetCsrf() {
  token = null;
}
export async function api<T>(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const method = options.method || "GET";
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  if (!["GET", "HEAD"].includes(method.toUpperCase())) {
    if (!token) {
      const csrf = await api<{ data: { csrf_token: string } }>("/auth/csrf");
      token = csrf.data.csrf_token;
    }
    headers.set("X-CSRFToken", token!);
  }
  const separator = path.includes("?") ? "&" : "?";
  let response: Response;
  try {
    response = await fetch(
      `/api/v1${path}${separator}lang=${i18n.global.locale.value}`,
      { ...options, headers, credentials: "same-origin" },
    );
  } catch {
    throw new ApiError("network_error");
  }
  let body;
  try {
    body = await response.json();
  } catch {
    throw new ApiError("server_error", response.status);
  }
  if (!response.ok) {
    if (body.error?.code === "csrf_failed" && retry) {
      resetCsrf();
      return api<T>(path, options, false);
    }
    if (response.status === 401 && body.error?.code === "unauthenticated") {
      window.dispatchEvent(new Event("learnhub:session-expired"));
    }
    throw new ApiError(
      body.error?.code || "server_error",
      response.status,
      body.error?.fields,
    );
  }
  return body as T;
}
export function json(method: string, body?: unknown): RequestInit {
  return {
    method,
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  };
}
