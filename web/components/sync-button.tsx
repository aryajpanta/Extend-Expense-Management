"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api";

export function SyncButton() {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => apiFetch("sync/run", { method: "POST" }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] }),
        queryClient.invalidateQueries({ queryKey: ["transactions"] }),
        queryClient.invalidateQueries({ queryKey: ["settings"] })
      ]);
    }
  });

  return (
    <button
      type="button"
      onClick={() => mutation.mutate()}
      className="rounded-full bg-ink px-5 py-3 text-sm font-medium text-white"
    >
      {mutation.isPending ? "Syncing..." : "Sync from Extend"}
    </button>
  );
}
