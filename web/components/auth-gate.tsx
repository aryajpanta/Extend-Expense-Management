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

  if (!sessionQuery.data?.authenticated) {
    return <div className="p-8 text-sm text-slate">Redirecting to login...</div>;
  }

  return <>{children}</>;
}

