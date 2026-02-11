import { Sidebar } from "@/components/layout/sidebar";
import { ChatWindow } from "@/components/chat/chat-window";

export default function HomePage() {
  return (
    <main className="flex h-screen overflow-hidden">
      <Sidebar />
      <section className="flex-1 p-4 md:p-6">
        <div className="mx-auto flex h-full w-full max-w-5xl flex-col">
          <header className="mb-4">
            <h2 className="text-xl font-semibold">ARIV Command Center</h2>
            <p className="text-sm text-muted">ChatGPT-inspired interface for secure control and configuration.</p>
          </header>
          <ChatWindow />
        </div>
      </section>
    </main>
  );
}
