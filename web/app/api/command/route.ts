import { NextResponse } from "next/server";
import { forwardToAriv } from "@/lib/ariv";
import { commandSchema, sanitizeText } from "@/lib/security";

export async function POST(request: Request) {
  try {
    const payload = commandSchema.parse(await request.json());

    const result = await forwardToAriv<{ output: string }>("/api/command", {
      method: "POST",
      body: JSON.stringify({
        command: sanitizeText(payload.command),
        sessionId: payload.sessionId
      })
    });

    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Invalid request" },
      { status: 400 }
    );
  }
}
