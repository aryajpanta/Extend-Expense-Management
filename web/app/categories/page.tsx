"use client";

import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { AppShell } from "@/components/app-shell";
import { ExpenseCategory, apiFetch } from "@/lib/api";

export default function CategoriesPage() {
  const queryClient = useQueryClient();
  const { data: categories } = useQuery({
    queryKey: ["expense-categories"],
    queryFn: () => apiFetch<ExpenseCategory[]>("expense-categories")
  });
  const [name, setName] = React.useState("");
  const [code, setCode] = React.useState("");
  const [required, setRequired] = React.useState(false);
  const createMutation = useMutation({
    mutationFn: () =>
      apiFetch("expense-categories", {
        method: "POST",
        body: JSON.stringify({
          name,
          code,
          required,
          active: true
        })
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["expense-categories"] });
      setName("");
      setCode("");
      setRequired(false);
    }
  });

  if (!categories) {
    return <div className="p-8 text-sm text-slate">Loading categories...</div>;
  }

  return (
    <AppShell
      heading="Categories"
      subheading="Keep your Extend expense taxonomy tidy without living in a full enterprise admin console."
    >
      <form
        className="mb-5 rounded-[28px] bg-white p-6 shadow-card"
        onSubmit={(event) => {
          event.preventDefault();
          createMutation.mutate();
        }}
      >
        <div className="grid gap-4 lg:grid-cols-[1fr_1fr_auto_auto]">
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Category name"
            className="rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
          />
          <input
            value={code}
            onChange={(event) => setCode(event.target.value)}
            placeholder="Category code"
            className="rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
          />
          <label className="flex items-center gap-2 rounded-2xl bg-fog px-4 py-3 text-sm">
            <input type="checkbox" checked={required} onChange={(event) => setRequired(event.target.checked)} />
            Required
          </label>
          <button className="rounded-full bg-pine px-5 py-3 text-sm font-medium text-white" type="submit">
            {createMutation.isPending ? "Creating..." : "Create category"}
          </button>
        </div>
      </form>
      <div className="grid gap-5 lg:grid-cols-2">
        {categories.map((category) => (
          <section key={category.id} className="rounded-[28px] bg-white p-6 shadow-card">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">
                  {category.name}
                </h2>
                <p className="mt-2 text-sm text-slate">{category.code}</p>
              </div>
              <div className="rounded-full bg-fog px-4 py-2 text-xs uppercase tracking-[0.18em] text-slate">
                {category.active ? "Active" : "Inactive"}
              </div>
            </div>
            <div className="mt-5 flex gap-3 text-sm text-slate">
              <span className="rounded-full bg-sand px-3 py-2">{category.required ? "Required" : "Optional"}</span>
              <span className="rounded-full bg-fog px-3 py-2">
                {category.freeTextAllowed ? "Free text enabled" : "Structured only"}
              </span>
            </div>
          </section>
        ))}
      </div>
    </AppShell>
  );
}
