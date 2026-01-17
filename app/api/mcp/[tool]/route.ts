import { NextResponse } from "next/server";

export const runtime = "nodejs";

const ALLOWED_TOOLS = new Set(["get_research", "generate_images"]);

export async function POST(
  request: Request,
  { params }: { params: { tool: string } }
) {
  const { tool } = params;
  if (!ALLOWED_TOOLS.has(tool)) {
    return NextResponse.json({ error: "Unknown MCP tool" }, { status: 404 });
  }

  const baseUrl = process.env.MCP_SERVER_URL ?? "http://127.0.0.1:8000";
  const targetUrl = `${baseUrl}/tools/${tool}`;

  try {
    const payload = await request.json();
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store"
    });

    const text = await response.text();
    if (!response.ok) {
      return NextResponse.json(
        {
          error: `MCP tool call failed (${response.status})`,
          detail: text
        },
        { status: 502 }
      );
    }

    return new NextResponse(text, {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      { error: "Failed to reach MCP server", detail },
      { status: 502 }
    );
  }
}
