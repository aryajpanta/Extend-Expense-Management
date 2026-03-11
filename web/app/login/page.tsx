"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { apiFetch } from "@/lib/api";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "owner@example.com",
      password: "change-me-now"
    }
  });

  const onSubmit = async (values: LoginForm) => {
    await apiFetch("auth/login", {
      method: "POST",
      body: JSON.stringify(values)
    });
    router.push("/dashboard");
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-[36px] bg-white shadow-card lg:grid-cols-[1.05fr_0.95fr]">
        <section className="bg-ink px-8 py-12 text-white lg:px-12">
          <div className="text-xs uppercase tracking-[0.24em] text-white/60">Expense Atlas</div>
          <h1 className="mt-5 font-['Iowan_Old_Style','Palatino_Linotype',serif] text-5xl font-semibold leading-tight">
            A personal command center for every Extend transaction.
          </h1>
          <p className="mt-6 max-w-md text-sm leading-7 text-white/72">
            Review charges, track missing receipts, clean up expense categories, and keep your own searchable local cache.
          </p>
        </section>
        <section className="px-8 py-12 lg:px-12">
          <div className="text-xs uppercase tracking-[0.24em] text-slate">Secure Access</div>
          <h2 className="mt-3 font-['Iowan_Old_Style','Palatino_Linotype',serif] text-4xl font-semibold text-ink">
            Sign in
          </h2>
          <form className="mt-8 space-y-5" onSubmit={handleSubmit(onSubmit)}>
            <label className="block">
              <span className="mb-2 block text-sm text-slate">Email</span>
              <input
                {...register("email")}
                className="w-full rounded-2xl border border-black/10 bg-fog px-4 py-3 outline-none ring-0 transition focus:border-pine"
              />
              {errors.email ? <span className="mt-2 block text-xs text-rust">{errors.email.message}</span> : null}
            </label>
            <label className="block">
              <span className="mb-2 block text-sm text-slate">Password</span>
              <input
                type="password"
                {...register("password")}
                className="w-full rounded-2xl border border-black/10 bg-fog px-4 py-3 outline-none ring-0 transition focus:border-pine"
              />
              {errors.password ? (
                <span className="mt-2 block text-xs text-rust">{errors.password.message}</span>
              ) : null}
            </label>
            <button
              disabled={isSubmitting}
              className="inline-flex rounded-full bg-pine px-6 py-3 text-sm font-medium text-white transition hover:opacity-90 disabled:opacity-50"
            >
              {isSubmitting ? "Signing in..." : "Enter workspace"}
            </button>
          </form>
        </section>
      </div>
    </main>
  );
}

