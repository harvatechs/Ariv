import { NextResponse } from "next/server";
import { forwardToAriv } from "@/lib/ariv";

export async function GET() {
  try {
    const logs = await forwardToAriv<{ entries: string[] }>("/api/logs", { method: "GET" });
    return NextResponse.json(logs);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch logs" },
      { status: 500 }
    );
  }
}
