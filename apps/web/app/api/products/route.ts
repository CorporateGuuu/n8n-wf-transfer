import { NextRequest, NextResponse } from "next/server";

import { createSessionApi, upstreamJson } from "../../../lib/session-api";

export async function GET(request: NextRequest) {
  const session = createSessionApi(request);
  const query = request.nextUrl.searchParams.toString();
  const upstream = await session.call(`/api/v1/products${query ? `?${query}` : ""}`);
  if (upstream.status === 401) return session.unauthorized();
  const body = await upstreamJson(upstream);
  return session.finalize(NextResponse.json(body, { status: upstream.status }));
}
