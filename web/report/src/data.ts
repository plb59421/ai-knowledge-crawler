import type { ReportPayload } from "./types";

const DATA_PATHS = [
  "/api/report",
  "/report-data/report_latest.json",
  "../data/report_latest.json"
];

export async function loadReportData(): Promise<ReportPayload> {
  const errors: string[] = [];
  for (const path of DATA_PATHS) {
    try {
      const response = await fetch(path, { cache: "no-store" });
      if (!response.ok) {
        errors.push(`${path}: ${response.status}`);
        continue;
      }
      return await response.json() as ReportPayload;
    } catch (error) {
      errors.push(`${path}: ${String(error)}`);
    }
  }
  throw new Error(`无法读取报告数据：${errors.join("; ")}`);
}
