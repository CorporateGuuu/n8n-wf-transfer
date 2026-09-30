import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.OPS_API_BASE_URL ?? "http://localhost:8000";
const refreshMaxAge = Number(process.env.REFRESH_TOKEN_TTL_SECONDS ?? 30 * 24 * 3600);

export async function POST(request: NextRequest) {
  const payload = await request.json();
  const upstream = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });
  const body = await upstream.json();
  if (!upstream.ok) return NextResponse.json(body, { status: upstream.status });

  const response = NextResponse.json({ ok: true });
  const secure = process.env.NODE_ENV === "production";
  response.cookies.set("ops_access", body.access_token, { httpOnly: true, sameSite: "lax", secure, path: "/", maxAge: body.expires_in });
  response.cookies.set("ops_refresh", body.refresh_token, { httpOnly: true, sameSite: "lax", secure, path: "/", maxAge: refreshMaxAge });
  return response;
}
