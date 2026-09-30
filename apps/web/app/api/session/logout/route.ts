import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.OPS_API_BASE_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  const refresh = request.cookies.get("ops_refresh")?.value;
  if (refresh) {
    await fetch(`${API_BASE}/api/v1/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
      cache: "no-store",
    }).catch(() => undefined);
  }
  const response = NextResponse.json({ ok: true });
  response.cookies.delete("ops_access");
  response.cookies.delete("ops_refresh");
  return response;
}
