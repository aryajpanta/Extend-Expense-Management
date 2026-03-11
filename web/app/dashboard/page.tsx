"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/app-shell";
import { StatCard } from "@/components/stat-card";
import { DashboardSummary, apiFetch, currency, friendlyDate } from "@/lib/api";
import { SyncButton } from "@/components/sync-button";

function TrendBars({
  title,
  items
}: {
  title: string;
  items: { label: string; amountCents: number }[];
}) {
  const max = Math.max(...items.map((item) => item.amountCents), 1);

  return (
    <section className="rounded-[28px] bg-white p-6 shadow-card">
      <div className="flex items-end justify-between">
        <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">{title}</h2>
        <span className="text-xs uppercase tracking-[0.2em] text-slate">Snapshot</span>
      </div>
      <div className="mt-6 space-y-4">
        {items.map((item) => (
          <div key={item.label}>
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="font-medium text-ink">{item.label}</span>
              <span className="text-slate">{currency(item.amountCents)}</span>
            </div>
            <div className="h-3 rounded-full bg-fog">
              <div
                className="h-3 rounded-full bg-pine"
                style={{ width: `${Math.max((item.amountCents / max) * 100, 6)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function DashboardPage() {
  const {
    data: summary,
    error,
    isLoading
  } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => apiFetch<DashboardSummary>("dashboard/summary"),
    retry: false
  });

  if (isLoading) {
    return <div className="p-8 text-sm text-slate">Loading dashboard...</div>;
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="rounded-2xl border border-rust/20 bg-rust/5 px-4 py-3 text-sm text-rust">
          Unable to load the dashboard right now. Refresh the page and try again.
        </div>
      </div>
    );
  }

  if (!summary) {
    return <div className="p-8 text-sm text-slate">Dashboard is empty right now.</div>;
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
      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <TrendBars title="Spend by day" items={summary.spendByDay} />
        <TrendBars title="Spend by status" items={summary.spendByStatus} />
      </div>
      <section className="mt-5 rounded-[28px] bg-white p-6 shadow-card">
        <div className="flex items-end justify-between">
          <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">Recent activity</h2>
          <Link href="/transactions" className="text-sm text-slate underline-offset-4 hover:underline">
            View all transactions
          </Link>
        </div>
        <div className="mt-5 space-y-3">
          {summary.recentTransactions.map((transaction) => (
            <Link
              key={transaction.id}
              href={`/transactions/${transaction.id}`}
              className="grid grid-cols-[1.2fr_0.8fr_0.7fr_0.4fr] items-center gap-4 rounded-2xl bg-fog px-4 py-4 text-sm transition hover:bg-sand/40"
            >
              <div>
                <div className="font-medium text-ink">{transaction.merchantName ?? "Unknown merchant"}</div>
                <div className="mt-1 text-slate">{friendlyDate(transaction.occurredAt)}</div>
              </div>
              <div className="text-slate">{transaction.status ?? "Unknown"}</div>
              <div className="text-slate">
                {transaction.receiptMissing
                  ? "Receipt missing"
                  : transaction.missingExpenseCategories
                    ? "Category missing"
                    : "In sync"}
              </div>
              <div className="text-right font-medium text-ink">{currency(transaction.amountCents)}</div>
            </Link>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
