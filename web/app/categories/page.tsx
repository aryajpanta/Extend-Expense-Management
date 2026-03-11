"use client";

import { AppShell } from "@/components/app-shell";
import { DashboardSummary, ExpenseCategory, apiFetch, currency } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

const researchedMappings = [
  { merchant: "Amazon / Amazon Marketplace", category: "Shopping" },
  { merchant: "HomeGoods", category: "Home" },
  { merchant: "Value Pet Vet", category: "Pets" },
  { merchant: "PMUSA / CITGO", category: "Gas" },
  { merchant: "MTA / OMNY", category: "Transit" },
  { merchant: "Walter AI", category: "Software" },
  { merchant: "T.J.Maxx", category: "Shopping" }
];

export default function CategoriesPage() {
  const { data: categories } = useQuery({
    queryKey: ["expense-categories"],
    queryFn: () => apiFetch<ExpenseCategory[]>("expense-categories")
  });
  const { data: dashboard } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => apiFetch<DashboardSummary>("dashboard/summary")
  });

  if (!categories || !dashboard) {
    return <div className="p-8 text-sm text-slate">Loading categories...</div>;
  }

  return (
    <AppShell
      heading="Categories"
      subheading="Extend categories stay read-only here. The app researches merchants locally and auto-applies a matching Extend category when one exists."
    >
      <section className="mb-5 rounded-[28px] bg-white p-6 shadow-card">
        <div className="text-xs uppercase tracking-[0.2em] text-slate">Status</div>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl bg-fog p-5">
            <div className="text-sm font-medium text-ink">Extend category creation is disabled in this app</div>
            <p className="mt-2 text-sm text-slate">
              Your account rejected category creation through the Extend API, so this screen now syncs and uses existing Extend categories only.
            </p>
          </div>
          <div className="rounded-2xl bg-fog p-5">
            <div className="text-sm font-medium text-ink">Automatic merchant categorization is still active</div>
            <p className="mt-2 text-sm text-slate">
              The app suggests a generic category from merchant research, then applies it to Extend expense data only when a matching Extend category is already available.
            </p>
          </div>
        </div>
      </section>

      <section className="mb-5 rounded-[28px] bg-white p-6 shadow-card">
        <div className="flex items-end justify-between">
          <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">Researched merchant buckets</h2>
          <span className="text-xs uppercase tracking-[0.2em] text-slate">Local intelligence</span>
        </div>
        <div className="mt-5 grid gap-3 lg:grid-cols-2">
          {researchedMappings.map((item) => (
            <div key={item.merchant} className="flex items-center justify-between rounded-2xl bg-fog px-4 py-4 text-sm">
              <span className="font-medium text-ink">{item.merchant}</span>
              <span className="rounded-full bg-white px-3 py-1 text-xs uppercase tracking-[0.16em] text-slate">
                {item.category}
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-5 rounded-[28px] bg-white p-6 shadow-card">
        <div className="flex items-end justify-between">
          <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">Current spending buckets</h2>
          <span className="text-xs uppercase tracking-[0.2em] text-slate">Dashboard snapshot</span>
        </div>
        <div className="mt-5 space-y-3">
          {dashboard.topCategories.length ? (
            dashboard.topCategories.map((bucket) => (
              <div key={bucket.label} className="flex items-center justify-between rounded-2xl bg-fog px-4 py-4 text-sm">
                <span className="font-medium text-ink">{bucket.label}</span>
                <span className="text-slate">{currency(bucket.amountCents)}</span>
              </div>
            ))
          ) : (
            <div className="rounded-2xl bg-fog px-4 py-4 text-sm text-slate">
              No categories have been applied or inferred yet.
            </div>
          )}
        </div>
      </section>

      <section className="rounded-[28px] bg-white p-6 shadow-card">
        <div className="flex items-end justify-between">
          <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">Synced Extend categories</h2>
          <span className="text-xs uppercase tracking-[0.2em] text-slate">{categories.length} categories</span>
        </div>
        <div className="mt-5 space-y-3">
          {categories.length ? (
            categories.map((category) => (
              <div key={category.id} className="flex items-center justify-between rounded-2xl bg-fog px-4 py-4 text-sm">
                <div>
                  <div className="font-medium text-ink">{category.name}</div>
                  <div className="mt-1 text-slate">{category.code}</div>
                </div>
                <div className="flex gap-2 text-xs uppercase tracking-[0.16em] text-slate">
                  <span className="rounded-full bg-white px-3 py-1">{category.active ? "Active" : "Inactive"}</span>
                  <span className="rounded-full bg-white px-3 py-1">{category.required ? "Required" : "Optional"}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-2xl border border-rust/20 bg-rust/5 px-4 py-4 text-sm text-rust">
              No Extend expense categories are available yet, so merchant suggestions stay local until matching categories exist in Extend.
            </div>
          )}
        </div>
      </section>
    </AppShell>
  );
}
