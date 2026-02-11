# ARIV Web Console (Next.js + Vercel)

Production-ready ChatGPT-inspired control plane for ARIV with authentication, API proxying, and secure defaults.

## Project structure

```text
web/
├── app/
│   ├── api/
│   │   ├── auth/[...nextauth]/route.ts
│   │   ├── command/route.ts
│   │   ├── config/route.ts
│   │   └── logs/route.ts
│   ├── settings/page.tsx
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── chat/chat-window.tsx
│   ├── layout/sidebar.tsx
│   └── ui/{button,input,switch,textarea}.tsx
├── lib/
│   ├── store/chat-store.ts
│   ├── ariv.ts
│   ├── env.ts
│   ├── rate-limit.ts
│   ├── security.ts
│   └── utils.ts
├── types/{index,next-auth}.d.ts
├── auth.ts
├── middleware.ts
├── .env.example
├── next.config.js
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

## Security controls included

- Auth.js (NextAuth v5) with GitHub/Google OAuth providers.
- JWT-backed sessions with protected API routes in middleware.
- Request throttling using a per-IP + per-route rate limiter.
- Command/config input validation using Zod schemas.
- Output/input sanitization for potentially unsafe content.
- Hardened response headers (CSP, X-Frame-Options, nosniff, etc.).
- Secrets only from environment variables.

## Local development

1. Install dependencies:
   ```bash
   cd web
   npm install
   ```
2. Configure env vars:
   ```bash
   cp .env.example .env.local
   ```
3. Run:
   ```bash
   npm run dev
   ```

## ARIV backend contract

The Next.js APIs are secure proxies and expect an ARIV backend service exposing:

- `POST /api/command` → `{ output: string }`
- `GET /api/config` / `PUT /api/config`
- `GET /api/logs` → `{ entries: string[] }`

Point `ARIV_API_BASE_URL` to this backend URL.

## Deploy to Vercel

1. Push repository.
2. Import the project in Vercel and set **Root Directory** to `web`.
3. Add env vars from `.env.example`:
   - `AUTH_SECRET` (required, min 32 chars)
   - OAuth provider keys
   - `ARIV_API_BASE_URL` (+ optional `ARIV_API_KEY`)
   - Rate limiting values
4. Deploy.

### Recommended production settings

- Restrict OAuth redirect domains to your production origin.
- Use managed Redis/Upstash for distributed rate limiting (replace in-memory limiter).
- Monitor logs and enable Vercel WAF + Bot Protection.
