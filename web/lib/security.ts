import { z } from "zod";

export const commandSchema = z.object({
  command: z
    .string()
    .min(1)
    .max(1200)
    .regex(/^[\w\s.,:;!?@#%+\-_=\/()\[\]{}"']+$/, "Invalid characters in command"),
  sessionId: z.string().uuid().optional()
});

export const configSchema = z.object({
  model: z.string().min(1).max(120),
  temperature: z.number().min(0).max(2),
  streaming: z.boolean(),
  safeMode: z.boolean(),
  telemetry: z.boolean()
});

export function sanitizeText(input: string) {
  return input.replace(/[<>]/g, "").trim();
}
