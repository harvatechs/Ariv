import { NextResponse } from "next/server";
import { forwardToAriv } from "@/lib/ariv";
import { configSchema } from "@/lib/security";

export async function GET() {
  try {
    const config = await forwardToAriv("/api/config", { method: "GET" });
    return NextResponse.json(config);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch config" },
      { status: 500 }
    );
  }
}

export async function PUT(request: Request) {
  try {
    const payload = configSchema.parse(await request.json());
    const updated = await forwardToAriv("/api/config", {
      method: "PUT",
      body: JSON.stringify(payload)
    });
    return NextResponse.json(updated);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to update config" },
      { status: 400 }
    );
  }
}
