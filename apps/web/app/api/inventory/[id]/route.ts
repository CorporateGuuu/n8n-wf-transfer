import { NextRequest, NextResponse } from "next/server";

import { createSessionApi, upstreamJson } from "../../../../lib/session-api";

export async function PATCH(request: NextRequest, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  const session = createSessionApi(request);
  const payload = await request.json();
  const upstream = await session.call(`/api/v1/inventory/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
  if (upstream.status === 401) return session.unauthorized();
  const body = await upstreamJson(upstream);
  return session.finalize(NextResponse.json(body, { status: upstream.status }));
}
