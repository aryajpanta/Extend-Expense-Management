const ENV_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

function resolveApiBaseUrl() {
  if (typeof window === "undefined") {
    return ENV_API_BASE_URL;
  }

  const url = new URL(ENV_API_BASE_URL);
  const isLocalApiHost = url.hostname === "localhost" || url.hostname === "127.0.0.1";
  const isLocalPageHost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

  // Keep API and page on the same local hostname so session cookies stay usable in dev.
  if (isLocalApiHost && isLocalPageHost && url.hostname !== window.location.hostname) {
    url.hostname = window.location.hostname;
  }

  return url.toString();
}

export class APIError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "APIError";
    this.status = status;
  }
}

type FetchOptions = RequestInit & {
  query?: Record<string, string | number | boolean | undefined>;
};

function buildUrl(path: string, query?: FetchOptions["query"]) {
  const url = new URL(path, `${resolveApiBaseUrl()}/`);
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
    throw new APIError(text || `Request failed with ${response.status}`, response.status);
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
  spendByDay: { label: string; amountCents: number }[];
  spendByStatus: { label: string; amountCents: number }[];
  recentTransactions: {
    id: string;
    merchantName: string | null;
    amountCents: number;
    status: string | null;
    occurredAt: string | null;
    receiptMissing: boolean;
    missingExpenseCategories: boolean;
  }[];
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
  suggestedCategoryName: string | null;
  suggestedCategoryReason: string | null;
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

export type MerchantRule = {
  id: number;
  matchType: string;
  pattern: string;
  categoryId: string;
  labelId: string | null;
  priority: number;
  active: boolean;
  categoryName: string;
  labelName: string | null;
};

export type MerchantRuleSeedResult = {
  categoriesCreated: number;
  rulesCreated: number;
  categoriesTotal: number;
  rulesTotal: number;
};

export type LoginPayload = {
  email: string;
  password: string;
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
