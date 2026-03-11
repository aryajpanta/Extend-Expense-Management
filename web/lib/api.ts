export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type FetchOptions = RequestInit & {
  query?: Record<string, string | number | boolean | undefined>;
};

function buildUrl(path: string, query?: FetchOptions["query"]) {
  const url = new URL(path, `${API_BASE_URL}/`);
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined || value === null || value === "") {
        return;
      }
      url.searchParams.set(key, String(value));
    });
  }
  return url.toString();
}

export async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
  const response = await fetch(buildUrl(path, options.query), {
    ...options,
    credentials: "include",
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export type SessionResponse = {
  authenticated: boolean;
  userEmail: string | null;
};

export type SyncRun = {
  id: number;
  status: string;
  startedAt: string;
  finishedAt: string | null;
  transactionsFetched: number;
  transactionsUpserted: number;
  errorMessage: string | null;
};

export type DashboardSummary = {
  totalSpendCents: number;
  transactionCount: number;
  receiptMissingCount: number;
  missingCategoryCount: number;
  topMerchants: { label: string; amountCents: number }[];
  topCategories: { label: string; amountCents: number }[];
  lastSyncAt: string | null;
};

export type TransactionListItem = {
  id: string;
  merchantName: string | null;
  merchantDescriptor: string | null;
  cardDisplayName: string | null;
  cardLast4: string | null;
  amountCents: number;
  direction: string;
  status: string | null;
  occurredAt: string | null;
  receiptMissing: boolean;
  attachmentsCount: number;
  missingExpenseCategories: boolean;
};

export type TransactionDetail = TransactionListItem & {
  rawExtendPayload: Record<string, unknown>;
  receipts: {
    id: string;
    contentType: string | null;
    uploadType: string | null;
    createdAt: string | null;
    urlOriginal: string | null;
    urlMain: string | null;
    urlThumbnail: string | null;
  }[];
  expenseDetails: {
    categoryId: string;
    labelId?: string | null;
  }[];
  notes: string | null;
  lastRefreshedAt: string | null;
};

export type TransactionListResponse = {
  items: TransactionListItem[];
  total: number;
  page: number;
  perPage: number;
};

export type ExpenseCategory = {
  id: string;
  name: string;
  code: string;
  active: boolean;
  required: boolean;
  freeTextAllowed: boolean | null;
};

export type ExpenseLabel = {
  id: string;
  categoryId: string;
  name: string;
  code: string;
  active: boolean;
};

export type SettingsPayload = {
  extendEnvironment: string;
  hasExtendCredentials: boolean;
  maskedExtendKey: string | null;
  latestSync: SyncRun | null;
};

export const currency = (amountCents: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD"
  }).format(amountCents / 100);

export const friendlyDate = (value: string | null) =>
  value ? new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : "Unknown";
