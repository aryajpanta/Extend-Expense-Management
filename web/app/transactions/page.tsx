"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/app-shell";
import { TransactionListResponse, apiFetch, currency, friendlyDate } from "@/lib/api";

export default function TransactionsPage() {
  const { data: response } = useQuery({
    queryKey: ["transactions"],
    queryFn: () =>
      apiFetch<TransactionListResponse>("transactions", {
        query: { per_page: 25, sort: "-date" }
      })
  });

  if (!response) {
    return <div className="p-8 text-sm text-slate">Loading transactions...</div>;
  }

  return (
    <AppShell
      heading="Transactions"
      subheading="Searchable local cache with the same list-first workflow you use in Extend."
    >
      <section className="overflow-hidden rounded-[28px] bg-white shadow-card">
        <div className="grid grid-cols-[1.1fr_1fr_0.7fr_0.65fr_0.4fr] gap-4 border-b border-black/5 px-6 py-4 text-xs uppercase tracking-[0.18em] text-slate">
          <span>Merchant</span>
          <span>Card</span>
          <span>Status</span>
          <span>Date</span>
          <span className="text-right">Amount</span>
        </div>
        <div>
          {response.items.map((transaction) => (
            <Link
              key={transaction.id}
              href={`/transactions/${transaction.id}`}
              className="grid grid-cols-[1.1fr_1fr_0.7fr_0.65fr_0.4fr] gap-4 border-b border-black/5 px-6 py-5 transition hover:bg-fog"
            >
              <div>
                <div className="font-medium text-ink">{transaction.merchantName ?? "Unknown merchant"}</div>
                <div className="mt-1 text-sm text-slate">
                  {transaction.receiptMissing ? "Receipt missing" : `${transaction.attachmentsCount} receipts`}
                </div>
              </div>
              <div className="text-sm text-slate">
                <div>{transaction.cardDisplayName ?? "Unknown card"}</div>
                <div>{transaction.cardLast4 ? `•••• ${transaction.cardLast4}` : "No last4"}</div>
              </div>
              <div className="text-sm text-slate">{transaction.status ?? "Unknown"}</div>
              <div className="text-sm text-slate">{friendlyDate(transaction.occurredAt)}</div>
              <div className="text-right font-medium text-ink">{currency(transaction.amountCents)}</div>
            </Link>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
