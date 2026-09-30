import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.OPS_API_BASE_URL ?? "http://localhost:8000";
const refreshMaxAge = Number(process.env.REFRESH_TOKEN_TTL_SECONDS ?? 30 * 24 * 3600);

type TokenBody = { access_token: string; refresh_token: string; expires_in: number };

export function createSessionApi(request: NextRequest) {
  let access = request.cookies.get("ops_access")?.value;
  const refresh = request.cookies.get("ops_refresh")?.value;
  let rotated: TokenBody | null = null;
  let refreshAttempted = false;

  async function rotate(): Promise<boolean> {
    if (!refresh || refreshAttempted) return false;
    refreshAttempted = true;
    const response = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
      cache: "no-store",
    });
    if (!response.ok) return false;
    rotated = await response.json();
    access = rotated!.access_token;
    return true;
  }

  async function call(path: string, init: RequestInit = {}): Promise<Response> {
    if (!access && !(await rotate())) {
      return new Response(JSON.stringify({ error: { message: "Authentication required" } }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    const headers = new Headers(init.headers);
    headers.set("Authorization", `Bearer ${access}`);
    if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");

    let response = await fetch(`${API_BASE}${path}`, { ...init, headers, cache: "no-store" });
    if (response.status === 401 && await rotate()) {
      headers.set("Authorization", `Bearer ${access}`);
      response = await fetch(`${API_BASE}${path}`, { ...init, headers, cache: "no-store" });
    }
    return response;
  }

  function finalize(response: NextResponse) {
    if (rotated) {
      const secure = process.env.NODE_ENV === "production";
      response.cookies.set("ops_access", rotated.access_token, {
        httpOnly: true,
        sameSite: "lax",
        secure,
        path: "/",
        maxAge: rotated.expires_in,
      });
      response.cookies.set("ops_refresh", rotated.refresh_token, {
        httpOnly: true,
        sameSite: "lax",
        secure,
        path: "/",
        maxAge: refreshMaxAge,
      });
    }
    return response;
  }

  function unauthorized(message = "Session expired") {
    const response = NextResponse.json({ error: { message } }, { status: 401 });
    response.cookies.delete("ops_access");
    response.cookies.delete("ops_refresh");
    return response;
  }

  return { call, finalize, unauthorized };
}

export async function upstreamJson(response: Response) {
  return response.json().catch(() => ({ error: { message: "Upstream API request failed" } }));
}
