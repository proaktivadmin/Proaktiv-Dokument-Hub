/**
 * V2 API Clients - Barrel Export
 */

export { mergeFieldsApi } from "./merge-fields";
export { codePatternsApi } from "./code-patterns";
export { layoutPartialsApi } from "./layout-partials";
export { templateAnalysisApi } from "./template-analysis";
export { templateSettingsApi } from "./template-settings";
export { dashboardApi } from "./dashboard";
export { storageApi } from "./storage";
export { authApi } from "./auth";

// Re-export from main api.ts for backwards compatibility
export { categoryApi, templateApi, analyticsApi } from "../api";

// Re-export types for convenience
export type { MergeFieldListParams } from "./merge-fields";
export type { CodePatternListParams } from "./code-patterns";
export type { LayoutPartialListParams } from "./layout-partials";
export type {
  StorageItem,
  BrowseResponse,
  StorageStatus,
  ImportToLibraryPayload,
  ImportResult,
  MovePayload,
} from "./storage";
export type { AuthStatus, AuthCheckResponse, LoginResponse } from "./auth";