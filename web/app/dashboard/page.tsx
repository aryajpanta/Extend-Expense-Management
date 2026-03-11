"use client";

import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/app-shell";
import { StatCard } from "@/components/stat-card";
import { DashboardSummary, apiFetch, currency, friendlyDate } from "@/lib/api";
import { SyncButton } from "@/components/sync-button";

export default function DashboardPage() {
  const { data: summary } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => apiFetch<DashboardSummary>("dashboard/summary")
  });

  if (!summary) {
    return <div className="p-8 text-sm text-slate">Loading dashboard...</div>;
  }

  return (
    <AppShell
      heading="Dashboard"
      subheading="A calmer, personal view of the same Extend activity you already track."
      action={<SyncButton />}
    >
      <div className="grid gap-5 lg:grid-cols-4">
        <StatCard label="Total Spend" value={summary.totalSpendCents} currencyValue />
        <StatCard label="Transactions" value={summary.transactionCount} />
        <StatCard label="Missing Receipts" value={summary.receiptMissingCount} />
        <StatCard label="Missing Categories" value={summary.missingCategoryCount} />
      </div>
      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <section className="rounded-[28px] bg-white p-6 shadow-card">
          <div className="flex items-end justify-between">
            <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">Top merchants</h2>
            <span className="text-xs uppercase tracking-[0.2em] text-slate">Current cache</span>
          </div>
          <div className="mt-6 space-y-4">
            {summary.topMerchants.map((merchant) => (
              <div key={merchant.label} className="flex items-center justify-between rounded-2xl bg-fog px-4 py-3">
                <span className="font-medium">{merchant.label}</span>
                <span className="text-slate">{currency(merchant.amountCents)}</span>
              </div>
            ))}
          </div>
        </section>
        <section className="rounded-[28px] bg-white p-6 shadow-card">
          <div className="flex items-end justify-between">
            <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">Top categories</h2>
            <span className="text-xs uppercase tracking-[0.2em] text-slate">
              {summary.lastSyncAt ? friendlyDate(summary.lastSyncAt) : "Not synced"}
            </span>
          </div>
          <div className="mt-6 space-y-4">
            {summary.topCategories.map((category) => (
              <div key={category.label} className="flex items-center justify-between rounded-2xl bg-fog px-4 py-3">
                <span className="font-medium">{category.label}</span>
                <span className="text-slate">{currency(category.amountCents)}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
