"use client";

import { useState } from "react";
import { v4 as uuid } from "uuid";
import { SendHorizontal } from "lucide-react";
import { useChatStore } from "@/lib/store/chat-store";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export function ChatWindow() {
  const { messages, addMessage } = useChatStore();
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);

  const submitCommand = async () => {
    if (!prompt.trim() || loading) return;

    const userMessage = {
      id: uuid(),
      role: "user" as const,
      content: prompt,
      createdAt: new Date().toISOString()
    };

    addMessage(userMessage);
    setLoading(true);

    try {
      const response = await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: prompt })
      });
      const data = await response.json();
      addMessage({
        id: uuid(),
        role: "assistant",
        content: data.output ?? data.error ?? "No response",
        createdAt: new Date().toISOString()
      });
    } catch (error) {
      addMessage({
        id: uuid(),
        role: "assistant",
        content: `Request failed: ${(error as Error).message}`,
        createdAt: new Date().toISOString()
      });
    } finally {
      setPrompt("");
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="mb-3 flex-1 space-y-3 overflow-y-auto rounded-lg border border-border bg-panel p-4">
        {messages.length === 0 ? (
          <p className="text-sm text-muted">Ask ARIV anything, run automation commands, or inspect system status.</p>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm ${
                msg.role === "user" ? "ml-auto bg-accent text-white" : "bg-black/30"
              }`}
            >
              {msg.content}
            </div>
          ))
        )}
      </div>

      <div className="rounded-lg border border-border bg-panel p-3">
        <div className="flex items-end gap-2">
          <Textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Send a command to ARIV..."
            className="min-h-[52px]"
          />
          <Button size="icon" onClick={submitCommand} disabled={loading}>
            <SendHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
