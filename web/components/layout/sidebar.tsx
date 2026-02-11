"use client";

import Link from "next/link";
import { Settings, PanelLeftClose, PanelLeftOpen, Shield } from "lucide-react";
import { useChatStore } from "@/lib/store/chat-store";
import { Button } from "@/components/ui/button";

export function Sidebar() {
  const { sidebarOpen, setSidebarOpen, messages } = useChatStore();

  return (
    <aside
      className={`border-r border-border bg-panel transition-all duration-200 ${
        sidebarOpen ? "w-72" : "w-16"
      }`}
    >
      <div className="flex h-full flex-col p-3">
        <div className="mb-4 flex items-center justify-between">
          {sidebarOpen ? <h1 className="text-sm font-semibold">ARIV</h1> : null}
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
          </Button>
        </div>

        {sidebarOpen ? (
          <>
            <div className="mb-3 flex items-center gap-2 text-xs text-muted">
              <Shield className="h-4 w-4" /> Secure session enabled
            </div>
            <nav className="space-y-2 text-sm">
              <Link href="/" className="block rounded-md px-3 py-2 hover:bg-white/5">
                Command Center
              </Link>
              <Link href="/settings" className="flex items-center gap-2 rounded-md px-3 py-2 hover:bg-white/5">
                <Settings className="h-4 w-4" /> Settings
              </Link>
            </nav>
            <div className="mt-4">
              <p className="mb-2 text-xs text-muted">History</p>
              <div className="space-y-1">
                {messages.slice(-6).map((msg) => (
                  <div key={msg.id} className="truncate rounded-md bg-black/20 px-2 py-1 text-xs text-muted">
                    {msg.content}
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : null}
      </div>
    </aside>
  );
}
