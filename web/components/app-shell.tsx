"use client";

import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, CreditCard, LayoutDashboard, RefreshCcw, Settings2 } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transactions", label: "Transactions", icon: CreditCard },
  { href: "/categories", label: "Categories", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings2 }
];

export function AppShell({
  children,
  heading,
  subheading,
  action
}: {
  children: React.ReactNode;
  heading: string;
  subheading?: string;
  action?: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-fog text-ink">
      <div className="grid min-h-screen lg:grid-cols-[260px_1fr]">
        <aside className="border-r border-black/5 bg-white">
          <div className="border-b border-black/5 px-6 py-6">
            <div className="text-xs uppercase tracking-[0.24em] text-slate">Extend</div>
            <div className="mt-2 font-['Iowan_Old_Style','Palatino_Linotype',serif] text-2xl font-semibold">
              Expense Atlas
            </div>
            <p className="mt-2 text-sm text-slate">A personal cashflow and receipt cockpit.</p>
          </div>
          <nav className="space-y-2 p-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={clsx(
                    "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition",
                    active ? "bg-ink text-white" : "text-slate hover:bg-fog hover:text-ink"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="mx-4 mt-8 rounded-3xl bg-sand/60 p-5 text-sm text-ink">
            <div className="flex items-center gap-2 font-medium">
              <RefreshCcw className="h-4 w-4" />
              Sync-aware
            </div>
            <p className="mt-2 text-slate">
              Your transaction cache stays local while Extend remains the source of truth.
            </p>
          </div>
        </aside>
        <main className="px-5 py-6 lg:px-8">
          <div className="mb-6 flex flex-col gap-4 rounded-[28px] bg-white px-6 py-5 shadow-card lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.24em] text-slate">Personal Workspace</div>
              <h1 className="mt-2 font-['Iowan_Old_Style','Palatino_Linotype',serif] text-4xl font-semibold">
                {heading}
              </h1>
              {subheading ? <p className="mt-2 text-sm text-slate">{subheading}</p> : null}
            </div>
            {action}
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}

