/**
 * API Clients - Barrel Export
 */

// V2 API Clients
export { mergeFieldsApi } from "./merge-fields";
export { codePatternsApi } from "./code-patterns";
export { layoutPartialsApi } from "./layout-partials";
export { templateAnalysisApi } from "./template-analysis";
export { templateSettingsApi } from "./template-settings";
export { dashboardApi } from "./dashboard";
export { storageApi } from "./storage";
export { authApi } from "./auth";

// V3 API Clients
export { officesApi } from "./offices";
export { employeesApi } from "./employees";
export { assetsApi } from "./assets";
export { territoriesApi } from "./territories";
export { checklistsApi } from "./checklists";
export { externalListingsApi } from "./external-listings";
export { syncApi } from "./sync";

// Vitec Integration
export { vitecApi } from "./vitec";

// Entra ID Sync
export { entraSyncApi } from "./entra-sync";

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
export type { OfficeListParams } from "./offices";
export type { EmployeeListParams } from "./employees";
export type { AssetListParams } from "./assets";
export type { TerritoryListParams } from "./territories";
export type { ChecklistTemplateListParams, ChecklistInstanceListParams } from "./checklists";
export type { ExternalListingListParams } from "./external-listings";
export type { VitecStatus, SyncPicturesResponse } from "./vitec";