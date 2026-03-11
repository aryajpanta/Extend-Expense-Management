"use client";

import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/app-shell";
import { SettingsPayload, apiFetch, friendlyDate } from "@/lib/api";

export default function SettingsPage() {
  const { data: settings } = useQuery({
    queryKey: ["settings"],
    queryFn: () => apiFetch<SettingsPayload>("settings")
  });

  if (!settings) {
    return <div className="p-8 text-sm text-slate">Loading settings...</div>;
  }

  return (
    <AppShell
      heading="Settings"
      subheading="Environment and sync diagnostics for your local deployment."
    >
      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-[28px] bg-white p-6 shadow-card">
          <div className="text-xs uppercase tracking-[0.2em] text-slate">Extend connection</div>
          <dl className="mt-5 space-y-4 text-sm">
            <div className="flex items-center justify-between rounded-2xl bg-fog px-4 py-3">
              <dt>Environment</dt>
              <dd>{settings.extendEnvironment}</dd>
            </div>
            <div className="flex items-center justify-between rounded-2xl bg-fog px-4 py-3">
              <dt>Credentials</dt>
              <dd>{settings.hasExtendCredentials ? settings.maskedExtendKey : "Missing"}</dd>
            </div>
          </dl>
        </section>
        <section className="rounded-[28px] bg-white p-6 shadow-card">
          <div className="text-xs uppercase tracking-[0.2em] text-slate">Latest sync</div>
          {settings.latestSync ? (
            <dl className="mt-5 space-y-4 text-sm">
              <div className="flex items-center justify-between rounded-2xl bg-fog px-4 py-3">
                <dt>Status</dt>
                <dd>{settings.latestSync.status}</dd>
              </div>
              <div className="flex items-center justify-between rounded-2xl bg-fog px-4 py-3">
                <dt>Finished</dt>
                <dd>{friendlyDate(settings.latestSync.finishedAt)}</dd>
              </div>
              <div className="flex items-center justify-between rounded-2xl bg-fog px-4 py-3">
                <dt>Transactions fetched</dt>
                <dd>{settings.latestSync.transactionsFetched}</dd>
              </div>
            </dl>
          ) : (
            <p className="mt-5 text-sm text-slate">No sync has completed yet.</p>
          )}
        </section>
      </div>
    </AppShell>
  );
}
