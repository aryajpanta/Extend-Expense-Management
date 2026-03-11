"use client";

import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Save, X } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { ExpenseCategory, ExpenseLabel, apiFetch } from "@/lib/api";

function CategoryLabels({ categoryId }: { categoryId: string }) {
  const queryClient = useQueryClient();
  const labelsQuery = useQuery({
    queryKey: ["expense-labels", categoryId],
    queryFn: () => apiFetch<ExpenseLabel[]>(`expense-categories/${categoryId}/labels`)
  });
  const [name, setName] = React.useState("");
  const [code, setCode] = React.useState("");
  const createLabelMutation = useMutation({
    mutationFn: () =>
      apiFetch(`expense-categories/${categoryId}/labels`, {
        method: "POST",
        body: JSON.stringify({
          name,
          code,
          active: true
        })
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["expense-labels", categoryId] });
      setName("");
      setCode("");
    }
  });

  return (
    <div className="mt-5 border-t border-black/5 pt-5">
      <div className="text-xs uppercase tracking-[0.18em] text-slate">Labels</div>
      <div className="mt-3 space-y-2">
        {labelsQuery.data?.map((label) => (
          <EditableLabelRow key={label.id} categoryId={categoryId} label={label} />
        ))}
        {!labelsQuery.data?.length ? <div className="text-sm text-slate">No labels yet.</div> : null}
      </div>
      <form
        className="mt-4 grid gap-3 lg:grid-cols-[1fr_1fr_auto]"
        onSubmit={(event) => {
          event.preventDefault();
          createLabelMutation.mutate();
        }}
      >
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="New label name"
          className="rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
        />
        <input
          value={code}
          onChange={(event) => setCode(event.target.value)}
          placeholder="New label code"
          className="rounded-2xl border border-black/10 bg-fog px-4 py-3 text-sm outline-none"
        />
        <button className="rounded-full bg-ink px-5 py-3 text-sm font-medium text-white" type="submit">
          {createLabelMutation.isPending ? "Creating..." : "Create label"}
        </button>
      </form>
    </div>
  );
}

function EditableLabelRow({ categoryId, label }: { categoryId: string; label: ExpenseLabel }) {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = React.useState(false);
  const [name, setName] = React.useState(label.name);
  const [active, setActive] = React.useState(label.active);

  React.useEffect(() => {
    setName(label.name);
    setActive(label.active);
  }, [label.active, label.name]);

  const updateMutation = useMutation({
    mutationFn: () =>
      apiFetch<ExpenseLabel>(`expense-categories/${categoryId}/labels/${label.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          name,
          active
        })
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["expense-labels", categoryId] });
      setIsEditing(false);
    }
  });

  if (!isEditing) {
    return (
      <div className="flex items-center justify-between rounded-2xl bg-fog px-4 py-3 text-sm">
        <div>
          <div className="font-medium text-ink">{label.name}</div>
          <div className="text-slate">{label.code}</div>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-white px-3 py-1 text-xs uppercase tracking-[0.16em] text-slate">
            {label.active ? "Active" : "Inactive"}
          </span>
          <button
            type="button"
            onClick={() => setIsEditing(true)}
            className="rounded-full border border-black/10 p-2 text-slate transition hover:bg-white hover:text-ink"
          >
            <Pencil className="h-4 w-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <form
      className="rounded-2xl bg-fog p-4"
      onSubmit={(event) => {
        event.preventDefault();
        updateMutation.mutate();
      }}
    >
      <div className="grid gap-3 lg:grid-cols-[1fr_auto_auto_auto]">
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          className="rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm outline-none"
        />
        <label className="flex items-center gap-2 rounded-2xl bg-white px-4 py-3 text-sm text-slate">
          <input type="checkbox" checked={active} onChange={(event) => setActive(event.target.checked)} />
          Active
        </label>
        <button className="rounded-full bg-ink px-4 py-3 text-sm font-medium text-white" type="submit">
          <span className="inline-flex items-center gap-2">
            <Save className="h-4 w-4" />
            {updateMutation.isPending ? "Saving..." : "Save"}
          </span>
        </button>
        <button
          type="button"
          onClick={() => {
            setName(label.name);
            setActive(label.active);
            setIsEditing(false);
          }}
          className="rounded-full border border-black/10 px-4 py-3 text-sm text-slate"
        >
          <span className="inline-flex items-center gap-2">
            <X className="h-4 w-4" />
            Cancel
          </span>
        </button>
      </div>
    </form>
  );
}

function CategoryCard({ category }: { category: ExpenseCategory }) {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = React.useState(false);
  const [name, setName] = React.useState(category.name);
  const [required, setRequired] = React.useState(category.required);
  const [active, setActive] = React.useState(category.active);
  const [freeTextAllowed, setFreeTextAllowed] = React.useState(Boolean(category.freeTextAllowed));

  React.useEffect(() => {
    setName(category.name);
    setRequired(category.required);
    setActive(category.active);
    setFreeTextAllowed(Boolean(category.freeTextAllowed));
  }, [category]);

  const updateMutation = useMutation({
    mutationFn: () =>
      apiFetch<ExpenseCategory>(`expense-categories/${category.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          name,
          required,
          active,
          freeTextAllowed
        })
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["expense-categories"] });
      setIsEditing(false);
    }
  });

  return (
    <section className="rounded-[28px] bg-white p-6 shadow-card">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">{category.name}</h2>
          <p className="mt-2 text-sm text-slate">{category.code}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="rounded-full bg-fog px-4 py-2 text-xs uppercase tracking-[0.18em] text-slate">
            {category.active ? "Active" : "Inactive"}
          </div>
          <button
            type="button"
            onClick={() => setIsEditing((value) => !value)}
            className="rounded-full border border-black/10 p-2 text-slate transition hover:bg-fog hover:text-ink"
          >
            <Pencil className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="mt-5 flex gap-3 text-sm text-slate">
        <span className="rounded-full bg-sand px-3 py-2">{category.required ? "Required" : "Optional"}</span>
        <span className="rounded-full bg-fog px-3 py-2">
          {category.freeTextAllowed ? "Free text enabled" : "Structured only"}
        </span>
      </div>
      {isEditing ? (
        <form
          className="mt-5 grid gap-3 rounded-3xl border border-black/5 bg-fog p-4"
          onSubmit={(event) => {
            event.preventDefault();
            updateMutation.mutate();
          }}
        >
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm outline-none"
          />
          <div className="grid gap-3 md:grid-cols-3">
            <label className="flex items-center gap-2 rounded-2xl bg-white px-4 py-3 text-sm text-slate">
              <input type="checkbox" checked={required} onChange={(event) => setRequired(event.target.checked)} />
              Required
            </label>
            <label className="flex items-center gap-2 rounded-2xl bg-white px-4 py-3 text-sm text-slate">
              <input type="checkbox" checked={active} onChange={(event) => setActive(event.target.checked)} />
              Active
            </label>
            <label className="flex items-center gap-2 rounded-2xl bg-white px-4 py-3 text-sm text-slate">
              <input
                type="checkbox"
                checked={freeTextAllowed}
                onChange={(event) => setFreeTextAllowed(event.target.checked)}
              />
              Free text allowed
            </label>
          </div>
          <div className="flex gap-3">
            <button className="rounded-full bg-pine px-5 py-3 text-sm font-medium text-white" type="submit">
              {updateMutation.isPending ? "Saving..." : "Save category"}
            </button>
            <button
              type="button"
              onClick={() => {
                setName(category.name);
                setRequired(category.required);
                setActive(category.active);
                setFreeTextAllowed(Boolean(category.freeTextAllowed));
                setIsEditing(false);
              }}
              className="rounded-full border border-black/10 px-5 py-3 text-sm text-slate"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : null}
      <CategoryLabels categoryId={category.id} />
    </section>
  );
}

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
          <CategoryCard key={category.id} category={category} />
        ))}
      </div>
    </AppShell>
  );
}
