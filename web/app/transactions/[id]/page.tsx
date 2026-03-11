"use client";

import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { AppShell } from "@/components/app-shell";
import { ExpenseCategory, ExpenseLabel, TransactionDetail, apiFetch, currency, friendlyDate } from "@/lib/api";

export default function TransactionDetailPage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = React.use(params);
  const queryClient = useQueryClient();
  const { data: transaction } = useQuery({
    queryKey: ["transaction", resolvedParams.id],
    queryFn: () => apiFetch<TransactionDetail>(`transactions/${resolvedParams.id}`)
  });
  const categoriesQuery = useQuery({
    queryKey: ["expense-categories"],
    queryFn: () => apiFetch<ExpenseCategory[]>("expense-categories")
  });
  const [categoryId, setCategoryId] = React.useState("");
  const [labelId, setLabelId] = React.useState("");
  const [receiptFile, setReceiptFile] = React.useState<File | null>(null);
  const labelsQuery = useQuery({
    queryKey: ["expense-labels", categoryId],
    queryFn: () => apiFetch<ExpenseLabel[]>(`expense-categories/${categoryId}/labels`),
    enabled: Boolean(categoryId)
  });

  React.useEffect(() => {
    const current = transaction?.expenseDetails[0];
    if (current?.categoryId) {
      setCategoryId(current.categoryId);
      setLabelId(current.labelId ?? "");
    }
  }, [transaction?.id, transaction?.expenseDetails]);

  const expenseMutation = useMutation({
    mutationFn: () =>
      apiFetch<TransactionDetail>(`transactions/${resolvedParams.id}/expense-data`, {
        method: "PATCH",
        body: JSON.stringify({
          expenseDetails: categoryId ? [{ categoryId, labelId: labelId || undefined }] : []
        })
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["transaction", resolvedParams.id] });
      await queryClient.invalidateQueries({ queryKey: ["transactions"] });
    }
  });

  const receiptMutation = useMutation({
    mutationFn: async () => {
      if (!receiptFile) {
        throw new Error("Choose a receipt file first");
      }
      const formData = new FormData();
      formData.append("file", receiptFile);
      return apiFetch(`transactions/${resolvedParams.id}/receipts`, {
        method: "POST",
        body: formData
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["transaction", resolvedParams.id] });
      await queryClient.invalidateQueries({ queryKey: ["transactions"] });
      setReceiptFile(null);
    }
  });

  if (!transaction) {
    return <div className="p-8 text-sm text-slate">Loading transaction...</div>;
  }

  return (
    <AppShell
      heading={transaction.merchantName ?? "Transaction"}
      subheading={`Last refreshed ${friendlyDate(transaction.lastRefreshedAt)}`}
    >
      <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[28px] bg-white p-6 shadow-card">
          <div className="flex items-start justify-between gap-6">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate">Amount</div>
              <div className="mt-2 font-['Iowan_Old_Style','Palatino_Linotype',serif] text-5xl font-semibold">
                {currency(transaction.amountCents)}
              </div>
            </div>
            <div className="rounded-full bg-fog px-4 py-2 text-sm text-slate">{transaction.status ?? "Unknown"}</div>
          </div>
          <dl className="mt-8 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl bg-fog p-4">
              <dt className="text-xs uppercase tracking-[0.18em] text-slate">Card</dt>
              <dd className="mt-2 text-sm">{transaction.cardDisplayName ?? "Unknown card"}</dd>
            </div>
            <div className="rounded-2xl bg-fog p-4">
              <dt className="text-xs uppercase tracking-[0.18em] text-slate">Date</dt>
              <dd className="mt-2 text-sm">{friendlyDate(transaction.occurredAt)}</dd>
            </div>
            <div className="rounded-2xl bg-fog p-4">
              <dt className="text-xs uppercase tracking-[0.18em] text-slate">Receipts</dt>
              <dd className="mt-2 text-sm">{transaction.receipts.length}</dd>
            </div>
            <div className="rounded-2xl bg-fog p-4">
              <dt className="text-xs uppercase tracking-[0.18em] text-slate">Expense lines</dt>
              <dd className="mt-2 text-sm">{transaction.expenseDetails.length}</dd>
            </div>
            <div className="rounded-2xl bg-fog p-4">
              <dt className="text-xs uppercase tracking-[0.18em] text-slate">Suggested category</dt>
              <dd className="mt-2 text-sm">{transaction.suggestedCategoryName ?? "No suggestion yet"}</dd>
            </div>
          </dl>
          {transaction.suggestedCategoryReason ? (
            <div className="mt-6 rounded-2xl border border-black/5 p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-slate">Merchant research</div>
              <p className="mt-2 text-sm text-slate">{transaction.suggestedCategoryReason}</p>
            </div>
          ) : null}
          {transaction.notes ? (
            <div className="mt-6 rounded-2xl border border-black/5 p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-slate">Notes</div>
              <p className="mt-2 text-sm text-slate">{transaction.notes}</p>
            </div>
          ) : null}
        </section>
        <section className="space-y-5">
          <div className="rounded-[28px] bg-white p-6 shadow-card">
            <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">Receipts</h2>
            <div className="mt-5 space-y-3">
              {transaction.receipts.map((receipt) => (
                <a
                  key={receipt.id}
                  href={receipt.urlOriginal ?? "#"}
                  className="flex items-center justify-between rounded-2xl bg-fog px-4 py-3 text-sm"
                >
                  <span>{receipt.contentType ?? "Receipt"}</span>
                  <span className="text-slate">{friendlyDate(receipt.createdAt)}</span>
                </a>
              ))}
            </div>
          </div>
          <div className="rounded-[28px] bg-white p-6 shadow-card">
            <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">Expense data</h2>
            <div className="mt-5 space-y-3">
              {transaction.expenseDetails.map((item, index) => (
                <div key={`${item.categoryId}-${index}`} className="rounded-2xl bg-fog px-4 py-3 text-sm">
                  Category:{" "}
                  {categoriesQuery.data?.find((category) => category.id === item.categoryId)?.name ?? item.categoryId}
                  {item.labelId
                    ? ` · Label: ${labelsQuery.data?.find((label) => label.id === item.labelId)?.name ?? item.labelId}`
                    : ""}
                </div>
              ))}
            </div>
            <form
              className="mt-5 space-y-3"
              onSubmit={(event) => {
                event.preventDefault();
                expenseMutation.mutate();
              }}
            >
              <select
                value={categoryId}
                onChange={(event) => setCategoryId(event.target.value)}
                className="w-full rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
              >
                <option value="">Select category</option>
                {categoriesQuery.data?.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
              <select
                value={labelId}
                onChange={(event) => setLabelId(event.target.value)}
                className="w-full rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
                disabled={!categoryId}
              >
                <option value="">No label</option>
                {labelsQuery.data?.map((label) => (
                  <option key={label.id} value={label.id}>
                    {label.name}
                  </option>
                ))}
              </select>
              <button className="rounded-full bg-pine px-5 py-3 text-sm font-medium text-white" type="submit">
                {expenseMutation.isPending ? "Saving..." : "Update expense data"}
              </button>
            </form>
          </div>
          <div className="rounded-[28px] bg-white p-6 shadow-card">
            <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">Upload receipt</h2>
            <form
              className="mt-5 space-y-3"
              onSubmit={(event) => {
                event.preventDefault();
                receiptMutation.mutate();
              }}
            >
              <input
                type="file"
                accept="image/*,application/pdf"
                onChange={(event) => setReceiptFile(event.target.files?.[0] ?? null)}
                className="block w-full rounded-2xl border border-dashed border-black/15 bg-fog px-4 py-4 text-sm"
              />
              <button className="rounded-full bg-ink px-5 py-3 text-sm font-medium text-white" type="submit">
                {receiptMutation.isPending ? "Uploading..." : "Upload receipt"}
              </button>
            </form>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
