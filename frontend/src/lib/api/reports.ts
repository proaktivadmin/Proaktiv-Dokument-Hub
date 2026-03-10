/**
 * Reports API
 *
 * Sales report and other downloadable reports.
 */

import { apiClient } from "./config";

export interface SalesReportParams {
  year?: number;
  department_id?: number;
}

/**
 * Download sales report as Excel file.
 * Returns blob for file download.
 */
export async function downloadSalesReport(params?: SalesReportParams): Promise<Blob> {
  const searchParams = new URLSearchParams();
  if (params?.year) searchParams.set("year", String(params.year));
  if (params?.department_id) searchParams.set("department_id", String(params.department_id));

  const url = `/reports/sales-report${searchParams.toString() ? `?${searchParams}` : ""}`;
  const response = await apiClient.get(url, {
    responseType: "blob",
  });

  if (response.status !== 200) {
    const text = await (response.data as Blob).text();
    let detail = "Kunne ikke laste ned rapporten.";
    try {
      const json = JSON.parse(text);
      detail = json.detail ?? detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }

  return response.data as Blob;
}
