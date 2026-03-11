import { currency } from "@/lib/api";

export function StatCard({
  label,
  value,
  currencyValue = false
}: {
  label: string;
  value: number;
  currencyValue?: boolean;
}) {
  return (
    <div className="rounded-[28px] bg-white p-6 shadow-card">
      <div className="text-xs uppercase tracking-[0.2em] text-slate">{label}</div>
      <div className="mt-3 font-['Iowan_Old_Style','Palatino_Linotype',serif] text-4xl font-semibold text-ink">
        {currencyValue ? currency(value) : value.toLocaleString("en-US")}
      </div>
    </div>
  );
}

