"use client";

import Link from "next/link";
import * as React from "react";
import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/app-shell";
import { TransactionListResponse, apiFetch, currency, friendlyDate } from "@/lib/api";

export default function TransactionsPage() {
  const [search, setSearch] = React.useState("");
  const [status, setStatus] = React.useState("");
  const [receiptMissing, setReceiptMissing] = React.useState(false);
  const [missingExpenseCategories, setMissingExpenseCategories] = React.useState(false);
  const [fromDate, setFromDate] = React.useState("");
  const [toDate, setToDate] = React.useState("");
  const [sort, setSort] = React.useState("-date");
  const { data: response } = useQuery({
    queryKey: ["transactions", search, status, receiptMissing, missingExpenseCategories, fromDate, toDate, sort],
    queryFn: () =>
      apiFetch<TransactionListResponse>("transactions", {
        query: {
          per_page: 25,
          sort,
          search: search || undefined,
          status: status || undefined,
          receipt_missing: receiptMissing || undefined,
          missing_expense_categories: missingExpenseCategories || undefined,
          from_date: fromDate || undefined,
          to_date: toDate || undefined
        }
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
      <section className="mb-5 rounded-[28px] bg-white p-6 shadow-card">
        <div className="grid gap-4 lg:grid-cols-[1.4fr_repeat(3,0.8fr)_auto_auto]">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search merchant, card, or descriptor"
            className="rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
          />
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            className="rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
          >
            <option value="">All statuses</option>
            <option value="PENDING">Pending</option>
            <option value="CLEARED">Cleared</option>
            <option value="DECLINED">Declined</option>
          </select>
          <input
            type="date"
            value={fromDate}
            onChange={(event) => setFromDate(event.target.value)}
            className="rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
          />
          <input
            type="date"
            value={toDate}
            onChange={(event) => setToDate(event.target.value)}
            className="rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
          />
          <select
            value={sort}
            onChange={(event) => setSort(event.target.value)}
            className="rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
          >
            <option value="-date">Newest first</option>
            <option value="date">Oldest first</option>
            <option value="-amount">Highest amount</option>
            <option value="amount">Lowest amount</option>
            <option value="merchant">Merchant A-Z</option>
            <option value="-merchant">Merchant Z-A</option>
          </select>
          <label className="flex items-center gap-2 rounded-2xl bg-fog px-4 py-3 text-sm text-slate">
            <input
              type="checkbox"
              checked={receiptMissing}
              onChange={(event) => setReceiptMissing(event.target.checked)}
            />
            Receipt missing
          </label>
          <label className="flex items-center gap-2 rounded-2xl bg-fog px-4 py-3 text-sm text-slate">
            <input
              type="checkbox"
              checked={missingExpenseCategories}
              onChange={(event) => setMissingExpenseCategories(event.target.checked)}
            />
            Category missing
          </label>
        </div>
        <div className="mt-4 text-sm text-slate">{response.total} cached transactions match your current filters.</div>
      </section>
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
