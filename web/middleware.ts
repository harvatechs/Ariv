import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { env } from "@/lib/env";
import { checkRateLimit } from "@/lib/rate-limit";

const protectedApiPaths = ["/api/command", "/api/config", "/api/logs"];

export default auth((req) => {
  const { pathname } = req.nextUrl;

  if (protectedApiPaths.some((path) => pathname.startsWith(path))) {
    if (!req.auth) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
    const key = `${ip}:${pathname}`;
    const result = checkRateLimit(key, env.RATE_LIMIT_WINDOW_MS, env.RATE_LIMIT_MAX_REQUESTS);

    if (!result.allowed) {
      return NextResponse.json(
        { error: "Too many requests", retryAfter: result.resetAt },
        { status: 429 }
      );
    }
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/api/:path*"]
};
