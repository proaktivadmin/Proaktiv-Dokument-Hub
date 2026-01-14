/**
 * V2 Hooks - Barrel Export
 */

export {
  useMergeFields,
  useMergeFieldCategories,
  useMergeFieldAutocomplete,
} from "./useMergeFields";

export { useCodePatterns, useCodePatternCategories } from "./useCodePatterns";

export { useLayoutPartials, useDefaultPartial } from "./useLayoutPartials";

export { useTemplateAnalysis } from "./useTemplateAnalysis";

export { useElementInspector } from "./useElementInspector";

export { useGroupedTemplates } from "./useGroupedTemplates";

// Re-export types
export type {
  UseMergeFieldsOptions,
  UseMergeFieldsResult,
  UseMergeFieldCategoriesResult,
  UseMergeFieldAutocompleteResult,
} from "./useMergeFields";

export type {
  UseCodePatternsOptions,
  UseCodePatternsResult,
  UseCodePatternCategoriesResult,
} from "./useCodePatterns";

export type { UseLayoutPartialsResult, UseDefaultPartialResult } from "./useLayoutPartials";

export type { UseTemplateAnalysisResult } from "./useTemplateAnalysis";

export type { UseElementInspectorResult } from "./useElementInspector";

export type { UseGroupedTemplatesResult } from "./useGroupedTemplates";
