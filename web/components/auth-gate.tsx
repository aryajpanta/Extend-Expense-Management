"use client";

import { useQuery } from "@tanstack/react-query";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { APIError, SessionResponse, apiFetch } from "@/lib/api";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const sessionQuery = useQuery({
    queryKey: ["session"],
    queryFn: () => apiFetch<SessionResponse>("auth/session"),
    retry: false
  });

  useEffect(() => {
    if (sessionQuery.error instanceof APIError && sessionQuery.error.status === 401) {
      const next = pathname ? `?next=${encodeURIComponent(pathname)}` : "";
      router.replace(`/login${next}`);
    }
  }, [pathname, router, sessionQuery.error]);

  if (sessionQuery.isLoading) {
    return <div className="p-8 text-sm text-slate">Checking session...</div>;
  }

  if (sessionQuery.isError) {
    if (sessionQuery.error instanceof APIError && sessionQuery.error.status === 401) {
      return <div className="p-8 text-sm text-slate">Redirecting to login...</div>;
    }
    return (
      <div className="p-8">
        <div className="rounded-2xl border border-rust/20 bg-rust/5 px-4 py-3 text-sm text-rust">
          Unable to verify your session right now. Refresh the page and try again.
        </div>
      </div>
    );
  }

  if (!sessionQuery.data?.authenticated) {
    return <div className="p-8 text-sm text-slate">Redirecting to login...</div>;
  }

  return <>{children}</>;
}
