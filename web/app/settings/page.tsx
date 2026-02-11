"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Sidebar } from "@/components/layout/sidebar";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useChatStore } from "@/lib/store/chat-store";

const formSchema = z.object({
  model: z.string().min(1),
  temperature: z.coerce.number().min(0).max(2),
  streaming: z.boolean(),
  safeMode: z.boolean(),
  telemetry: z.boolean()
});

type FormData = z.infer<typeof formSchema>;

export default function SettingsPage() {
  const { config, setConfig } = useChatStore();
  const [status, setStatus] = useState<string>("");

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: config
  });

  useEffect(() => {
    form.reset(config);
  }, [config, form]);

  const onSubmit = form.handleSubmit(async (values) => {
    const res = await fetch("/api/config", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values)
    });

    if (!res.ok) {
      setStatus("Failed to save settings.");
      return;
    }

    setConfig(values);
    setStatus("Configuration saved securely.");
  });

  return (
    <main className="flex h-screen overflow-hidden">
      <Sidebar />
      <section className="flex-1 p-4 md:p-6">
        <div className="mx-auto max-w-2xl rounded-xl border border-border bg-panel p-6">
          <h2 className="mb-1 text-xl font-semibold">ARIV Configuration</h2>
          <p className="mb-6 text-sm text-muted">Manage model behavior and safety settings.</p>

          <form onSubmit={onSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm">Model Name</label>
              <Input {...form.register("model")} />
            </div>

            <div>
              <label className="mb-2 block text-sm">Temperature</label>
              <Input type="number" step="0.1" min="0" max="2" {...form.register("temperature")} />
            </div>

            <div className="flex items-center justify-between rounded-md border border-border p-3">
              <span className="text-sm">Enable Streaming Responses</span>
              <Switch checked={form.watch("streaming")} onCheckedChange={(v) => form.setValue("streaming", v)} />
            </div>

            <div className="flex items-center justify-between rounded-md border border-border p-3">
              <span className="text-sm">Safe Mode (recommended)</span>
              <Switch checked={form.watch("safeMode")} onCheckedChange={(v) => form.setValue("safeMode", v)} />
            </div>

            <div className="flex items-center justify-between rounded-md border border-border p-3">
              <span className="text-sm">Telemetry</span>
              <Switch checked={form.watch("telemetry")} onCheckedChange={(v) => form.setValue("telemetry", v)} />
            </div>

            <Button type="submit">Save Configuration</Button>
            {status ? <p className="text-sm text-muted">{status}</p> : null}
          </form>
        </div>
      </section>
    </main>
  );
}
