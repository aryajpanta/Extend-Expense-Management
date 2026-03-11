"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";

export function LogoutButton() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => apiFetch("auth/logout", { method: "POST" }),
    onSuccess: async () => {
      await queryClient.clear();
      router.replace("/login");
    }
  });

  return (
    <button
      type="button"
      onClick={() => mutation.mutate()}
      className="rounded-full border border-black/10 px-4 py-2 text-sm text-slate transition hover:bg-fog hover:text-ink"
    >
      {mutation.isPending ? "Signing out..." : "Sign out"}
    </button>
  );
}
