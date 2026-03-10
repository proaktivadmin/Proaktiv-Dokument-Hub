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

    return response.data as Blob;
  } catch (err) {
    const axiosErr = err as { response?: { data?: Blob | string; status?: number } };
    const data = axiosErr.response?.data;
    let detail = "Kunne ikke laste ned rapporten.";
    if (data) {
      try {
        const text = typeof data === "string" ? data : await (data as Blob).text();
        const json = JSON.parse(text) as { detail?: string };
        if (json.detail) detail = json.detail;
      } catch {
        // ignore
      }
    }
    throw new Error(detail);
  }
}
