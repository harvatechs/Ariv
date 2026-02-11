import { create } from "zustand";
import type { ArivConfig, ChatMessage } from "@/types";

type ChatState = {
  messages: ChatMessage[];
  config: ArivConfig;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  addMessage: (message: ChatMessage) => void;
  setConfig: (config: ArivConfig) => void;
};

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  sidebarOpen: true,
  config: {
    model: "ariv-default",
    temperature: 0.7,
    streaming: true,
    safeMode: true,
    telemetry: false
  },
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setConfig: (config) => set({ config })
}));
