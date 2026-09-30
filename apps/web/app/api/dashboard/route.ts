import { NextRequest, NextResponse } from "next/server";

import { createSessionApi, upstreamJson } from "../../../lib/session-api";

export async function GET(request: NextRequest) {
  const session = createSessionApi(request);
  const endpoints = [
    ["me", "/api/v1/me"],
    ["kpis", "/api/v1/analytics/kpis"],
    ["inventory", "/api/v1/inventory?page=1&page_size=10&sort=updated_at&order=desc"],
    ["products", "/api/v1/products?page=1&page_size=50&sort=sku&order=asc"],
    ["activity", "/api/v1/audit-events?page=1&page_size=8"],
  ] as const;

  const data: Record<string, unknown> = {};
  for (const [key, path] of endpoints) {
    const upstream = await session.call(path);
    if (upstream.status === 401) return session.unauthorized();
    if (!upstream.ok) return session.finalize(NextResponse.json(await upstreamJson(upstream), { status: upstream.status }));
    data[key] = await upstream.json();
  }

  return session.finalize(NextResponse.json(data));
}
