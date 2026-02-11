export type ChatRole = "user" | "assistant" | "system";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
};

export type ArivConfig = {
  model: string;
  temperature: number;
  streaming: boolean;
  safeMode: boolean;
  telemetry: boolean;
};
