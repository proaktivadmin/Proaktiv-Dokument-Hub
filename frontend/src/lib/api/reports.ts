/**
 * Reports API
 *
 * Sales report and other downloadable reports.
 */

import { apiClient } from "./config";

export interface SalesReportParams {
  year?: number;
  department_id?: number;
  from_date?: string; // YYYY-MM-DD
  to_date?: string; // YYYY-MM-DD
  include_vat?: boolean;
}

export interface SalesReportTransaction {
  posting_date: string;
  account: string;
  description: string;
  amount: number;
}

export interface SalesReportProperty {
  address: string;
  estate_id: string;
  assignment_number?: string;
  property_type: string;
  assignment_type: string;
  total: number;
  transactions: SalesReportTransaction[];
}

export interface SalesReportBroker {
  broker_id: string;
  name: string;
  sale_count: number;
  total: number;
  properties: SalesReportProperty[];
}

export interface ReportDataSourceInfo {
  name: string;
  label: string;
  coverage: string;
  row_count: number;
}

export interface ReportScopeMetadata {
  accounts_included: string[];
  account_categories: Record<string, string[]>;
  estate_statuses: string;
  vat_handling: string;
  date_range: { from: string; to: string };
  department_filter: number | null;
  last_synced_at: string | null;
  data_sources: ReportDataSourceInfo[];
  brokers_filter: string;
  data_freshness_note: string;
  validation_warnings_count: number;
}

export interface SalesReportData {
  year: number;
  department_id: number;
  from_date: string;
  to_date: string;
  from_date_display: string;
  to_date_display: string;
  include_vat: boolean;
  brokers: SalesReportBroker[];
  total_sales: number;
  total_revenue: number;
  scope?: ReportScopeMetadata;
}

export interface FranchiseDepartment {
  department_id: number;
  department_name: string;
  total_sales: number;
  total_revenue: number;
  revenue_share_percent: number;
  brokers: SalesReportBroker[];
}

export interface FranchiseReportData {
  year: number;
  from_date: string;
  to_date: string;
  from_date_display: string;
  to_date_display: string;
  include_vat: boolean;
  summary: {
    total_sales: number;
    total_revenue: number;
    department_count: number;
  };
  departments: FranchiseDepartment[];
}

export interface PerformerProperty {
  address: string;
  estate_id: string;
  assignment_number?: string;
  property_type: string;
  assignment_type: string;
  total: number;
  transactions: SalesReportTransaction[];
}

export interface PerformerRow {
  broker_id?: string;
  name?: string;
  department_id?: number;
  department_name?: string;
  total_sales?: number;
  total_revenue?: number;
  total?: number;
  sale_count?: number;
  properties?: PerformerProperty[];
  brokers?: PerformerRow[];
}

export interface BestPerformersData {
  from_date: string;
  to_date: string;
  from_date_display: string;
  to_date_display: string;
  include_vat: boolean;
  top_n: number;
  eiendomsmegler: PerformerRow[];
  eiendomsmeglerfullmektig: PerformerRow[];
  unknown: PerformerRow[];
  departments: PerformerRow[];
}

export interface ReportBudget {
  id: string;
  department_id: number;
  year: number;
  month: number | null;
  budget_amount: number;
  created_at: string;
  updated_at: string;
}

export interface BudgetComparisonMonth {
  month: number;
  actual: number;
  budget: number;
  variance: number;
  achieved_percent: number;
}

export interface BudgetComparisonData {
  department_id: number;
  year: number;
  include_vat: boolean;
  months: BudgetComparisonMonth[];
  ytd_actual: number;
  ytd_budget: number;
  ytd_variance: number;
  ytd_achieved_percent: number;
  projected_year_end: number;
  status: "On track" | "Behind" | "Ahead";
}

export interface ReportSubscription {
  id: string;
  name: string;
  report_type: "best_performers" | "franchise_summary";
  cadence: "weekly" | "monthly";
  recipients: string[];
  department_ids: number[];
  include_vat: boolean;
  day_of_week: number;
  day_of_month: number;
  send_hour: number;
  timezone: string;
  is_active: boolean;
  last_run_at: string | null;
  next_run_at: string | null;
  last_status: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReportSalesSyncEvent {
  id: number;
  installation_id: string;
  department_id: number;
  event_type: string;
  from_date: string;
  to_date: string;
  estates_upserted: number;
  transactions_upserted: number;
  payload: Record<string, unknown>;
  created_at: string;
}

/**
 * Fetch sales report data as JSON for dashboard display.
 */
export async function fetchSalesReportData(
  params?: SalesReportParams
): Promise<SalesReportData> {
  const searchParams = new URLSearchParams();
  if (params?.year) searchParams.set("year", String(params.year));
  if (params?.department_id) searchParams.set("department_id", String(params.department_id));
  if (params?.from_date) searchParams.set("from_date", params.from_date);
  if (params?.to_date) searchParams.set("to_date", params.to_date);
  if (params?.include_vat) searchParams.set("include_vat", "true");

  const url = `/reports/sales-report/data${searchParams.toString() ? `?${searchParams}` : ""}`;
  const response = await apiClient.get<SalesReportData>(url);
  return response.data;
}

/**
 * Download sales report as Excel file.
 * Returns blob for file download.
 */
export async function downloadSalesReport(params?: SalesReportParams): Promise<Blob> {
  const searchParams = new URLSearchParams();
  if (params?.year) searchParams.set("year", String(params.year));
  if (params?.department_id) searchParams.set("department_id", String(params.department_id));
  if (params?.from_date) searchParams.set("from_date", params.from_date);
  if (params?.to_date) searchParams.set("to_date", params.to_date);
  if (params?.include_vat) searchParams.set("include_vat", "true");

  const url = `/reports/sales-report${searchParams.toString() ? `?${searchParams}` : ""}`;
  try {
    const response = await apiClient.get(url, {
      responseType: "blob",
      validateStatus: (status) => status === 200,
    });

    const blob = response.data as Blob;
    if (!blob || blob.size === 0) {
      throw new Error("Tom fil mottatt fra serveren.");
    }
    // xlsx files are ZIP archives (magic bytes PK)
    const header = await blob.slice(0, 4).arrayBuffer();
    const bytes = new Uint8Array(header);
    if (bytes[0] !== 0x50 || bytes[1] !== 0x4b) {
      const preview = await blob.slice(0, 200).text();
      if (preview.trim().startsWith("{") || preview.trim().startsWith("<")) {
        let msg = "Server returnerte feil i stedet for Excel-fil.";
        try {
          const json = JSON.parse(preview) as { detail?: string };
          if (json.detail) msg = json.detail;
        } catch {
          /* ignore */
        }
        throw new Error(msg);
      }
    }
    return blob;
  } catch (err) {
    if (err instanceof Error && !(err as { response?: unknown }).response) {
      throw err;
    }
    const axiosErr = err as { response?: { data?: Blob | string; status?: number } };
    const data = axiosErr.response?.data;
    let detail = "Kunne ikke laste ned rapporten.";
    if (data) {
      try {
        const text = typeof data === "string" ? data : await (data as Blob).text();
        const json = JSON.parse(text) as { detail?: string };
        if (json.detail) detail = json.detail;
      } catch {
        /* ignore */
      }
    }
    throw new Error(detail);
  }
}

export async function fetchFranchiseReportData(params?: SalesReportParams): Promise<FranchiseReportData> {
  const searchParams = new URLSearchParams();
  if (params?.year) searchParams.set("year", String(params.year));
  if (params?.from_date) searchParams.set("from_date", params.from_date);
  if (params?.to_date) searchParams.set("to_date", params.to_date);
  if (params?.include_vat) searchParams.set("include_vat", "true");
  const url = `/reports/sales-report/franchise${searchParams.toString() ? `?${searchParams}` : ""}`;
  const response = await apiClient.get<FranchiseReportData>(url);
  return response.data;
}

export async function fetchBestPerformers(params?: SalesReportParams & { top_n?: number }): Promise<BestPerformersData> {
  const searchParams = new URLSearchParams();
  if (params?.year) searchParams.set("year", String(params.year));
  if (params?.from_date) searchParams.set("from_date", params.from_date);
  if (params?.to_date) searchParams.set("to_date", params.to_date);
  if (params?.include_vat) searchParams.set("include_vat", "true");
  if (params?.top_n) searchParams.set("top_n", String(params.top_n));
  const url = `/reports/best-performers${searchParams.toString() ? `?${searchParams}` : ""}`;
  const response = await apiClient.get<BestPerformersData>(url);
  return response.data;
}

export async function downloadBestPerformers(params?: SalesReportParams & { top_n?: number }): Promise<Blob> {
  const searchParams = new URLSearchParams();
  if (params?.year) searchParams.set("year", String(params.year));
  if (params?.from_date) searchParams.set("from_date", params.from_date);
  if (params?.to_date) searchParams.set("to_date", params.to_date);
  if (params?.include_vat) searchParams.set("include_vat", "true");
  if (params?.top_n) searchParams.set("top_n", String(params.top_n));
  const url = `/reports/best-performers/export${searchParams.toString() ? `?${searchParams}` : ""}`;
  const response = await apiClient.get(url, { responseType: "blob" });
  return response.data as Blob;
}

export async function listReportBudgets(params?: { department_id?: number; year?: number }): Promise<ReportBudget[]> {
  const searchParams = new URLSearchParams();
  if (params?.department_id) searchParams.set("department_id", String(params.department_id));
  if (params?.year) searchParams.set("year", String(params.year));
  const url = `/reports/budgets${searchParams.toString() ? `?${searchParams}` : ""}`;
  const response = await apiClient.get<ReportBudget[]>(url);
  return response.data;
}

export async function upsertReportBudget(payload: {
  department_id: number;
  year: number;
  month: number | null;
  budget_amount: number;
}): Promise<ReportBudget> {
  const response = await apiClient.post<ReportBudget>("/reports/budgets", payload);
  return response.data;
}

export async function getBudgetComparison(params: {
  department_id: number;
  year: number;
  include_vat?: boolean;
}): Promise<BudgetComparisonData> {
  const searchParams = new URLSearchParams();
  searchParams.set("department_id", String(params.department_id));
  searchParams.set("year", String(params.year));
  if (params.include_vat) searchParams.set("include_vat", "true");
  const response = await apiClient.get<BudgetComparisonData>(`/reports/budgets/comparison?${searchParams}`);
  return response.data;
}

export async function listReportSubscriptions(active_only?: boolean): Promise<ReportSubscription[]> {
  const searchParams = new URLSearchParams();
  if (active_only) searchParams.set("active_only", "true");
  const response = await apiClient.get<ReportSubscription[]>(
    `/reports/subscriptions${searchParams.toString() ? `?${searchParams}` : ""}`
  );
  return response.data;
}

export async function createReportSubscription(payload: Omit<ReportSubscription, "id" | "created_at" | "updated_at" | "last_run_at" | "next_run_at" | "last_status" | "last_error">): Promise<ReportSubscription> {
  const response = await apiClient.post<ReportSubscription>("/reports/subscriptions", payload);
  return response.data;
}

export async function updateReportSubscription(
  id: string,
  payload: Omit<ReportSubscription, "id" | "created_at" | "updated_at" | "last_run_at" | "next_run_at" | "last_status" | "last_error">
): Promise<ReportSubscription> {
  const response = await apiClient.put<ReportSubscription>(`/reports/subscriptions/${id}`, payload);
  return response.data;
}

export async function deleteReportSubscription(id: string): Promise<void> {
  await apiClient.delete(`/reports/subscriptions/${id}`);
}

export async function testReportSubscription(id: string, recipient?: string): Promise<void> {
  const searchParams = new URLSearchParams();
  if (recipient) searchParams.set("recipient", recipient);
  await apiClient.post(`/reports/subscriptions/${id}/test-send${searchParams.toString() ? `?${searchParams}` : ""}`);
}


export async function listReportCacheEvents(params?: {
  department_id?: number;
  since_id?: number;
  limit?: number;
}): Promise<ReportSalesSyncEvent[]> {
  const searchParams = new URLSearchParams();
  if (params?.department_id) searchParams.set("department_id", String(params.department_id));
  if (params?.since_id) searchParams.set("since_id", String(params.since_id));
  if (params?.limit) searchParams.set("limit", String(params.limit));
  const response = await apiClient.get<ReportSalesSyncEvent[]>(
    `/reports/cache-events${searchParams.toString() ? `?${searchParams}` : ""}`
  );
  return response.data;
}

export function buildReportCacheEventsStreamUrl(params?: {
  department_id?: number;
  since_id?: number;
  poll_interval_seconds?: number;
  max_seconds?: number;
}): string {
  const searchParams = new URLSearchParams();
  if (params?.department_id) searchParams.set("department_id", String(params.department_id));
  if (params?.since_id) searchParams.set("since_id", String(params.since_id));
  if (params?.poll_interval_seconds) searchParams.set("poll_interval_seconds", String(params.poll_interval_seconds));
  if (params?.max_seconds) searchParams.set("max_seconds", String(params.max_seconds));
  const suffix = searchParams.toString() ? `?${searchParams}` : "";
  return `/api/reports/cache-events/stream${suffix}`;
}
