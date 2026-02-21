"use client";

import { useState, useMemo, useCallback } from "react";
import { Variable, Wand2, List, Search } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { CategorySidebar } from "@/components/flettekoder/CategorySidebar";
import { MergeFieldGrid } from "@/components/flettekoder/MergeFieldGrid";
import { MergeFieldCard } from "@/components/flettekoder/MergeFieldCard";
import { CodeGenerator } from "@/components/flettekoder/CodeGenerator";
import {
  useMergeFields,
  useMergeFieldCategories,
  useMergeFieldAutocomplete,
} from "@/hooks/v2";
import type { MergeField } from "@/types/v2";
import { useToast } from "@/hooks/use-toast";

interface MergeFieldPanelProps {
  onInsert: (text: string) => void;
  currentContent: string;
  templateId?: string;
}

const MERGE_FIELD_REGEX = /\[\[([^\]]+)\]\]/g;

function extractMergeFields(html: string): string[] {
  const fields: string[] = [];
  let match;
  const regex = new RegExp(MERGE_FIELD_REGEX.source, "g");
  while ((match = regex.exec(html)) !== null) {
    if (!fields.includes(match[1])) {
      fields.push(match[1]);
    }
  }
  return fields;
}

function FieldBrowserTab({
  onInsert,
}: {
  onInsert: (text: string) => void;
}) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const { toast } = useToast();

  const { categories, isLoading: categoriesLoading } =
    useMergeFieldCategories();
  const { fields, total, isLoading: fieldsLoading } = useMergeFields({
    category: selectedCategory || undefined,
    search: searchQuery || undefined,
    perPage: 50,
  });

  const { suggestions } = useMergeFieldAutocomplete(searchQuery);
  const showSuggestions = searchQuery.length >= 2 && suggestions.length > 0;

  const handleFieldClick = useCallback(
    (field: MergeField) => {
      const syntax = `[[${field.path}]]`;
      onInsert(syntax);
      toast({
        title: "Flettekode satt inn",
        description: syntax,
      });
    },
    [onInsert, toast]
  );

  return (
    <div className="flex flex-col h-full gap-3">
      {/* Search */}
      <div className="relative shrink-0">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          type="search"
          placeholder="Søk flettekoder..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 bg-white/80 backdrop-blur-sm"
        />
        {showSuggestions && (
          <div className="absolute z-50 mt-1 w-full rounded-lg border bg-white shadow-elevated max-h-48 overflow-y-auto">
            {suggestions.map((field) => (
              <button
                key={field.id}
                className="w-full flex flex-col items-start px-3 py-2 text-left hover:bg-gray-50 border-b last:border-b-0 transition-colors"
                onClick={() => {
                  handleFieldClick(field);
                  setSearchQuery("");
                }}
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm text-[#272630]">
                    {field.label}
                  </span>
                  <code className="text-xs text-gray-500 bg-gray-100 px-1 rounded">
                    {field.path}
                  </code>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex gap-3 flex-1 min-h-0 overflow-hidden">
        {/* Category sidebar — compact for panel */}
        <aside className="shrink-0 overflow-y-auto">
          <CategorySidebar
            categories={categories}
            selectedCategory={selectedCategory}
            onSelect={setSelectedCategory}
            isLoading={categoriesLoading}
          />
        </aside>

        {/* Grid */}
        <div className="flex-1 overflow-y-auto min-w-0">
          <MergeFieldGrid
            fields={fields}
            isLoading={fieldsLoading}
            onFieldClick={handleFieldClick}
          />
          <div className="mt-2 text-xs text-gray-500">{total} flettekoder</div>
        </div>
      </div>
    </div>
  );
}

function InUseTab({
  currentContent,
  onInsert,
}: {
  currentContent: string;
  onInsert: (text: string) => void;
}) {
  const { toast } = useToast();
  const { fields: allFields } = useMergeFields({ perPage: 500 });

  const usedFieldPaths = useMemo(
    () => extractMergeFields(currentContent),
    [currentContent]
  );

  const usedFieldsWithMeta = useMemo(() => {
    const fieldMap = new Map(allFields.map((f) => [f.path, f]));
    return usedFieldPaths.map((path) => ({
      path,
      field: fieldMap.get(path) || null,
    }));
  }, [usedFieldPaths, allFields]);

  const grouped = useMemo(() => {
    const groups: Record<string, typeof usedFieldsWithMeta> = {};
    for (const item of usedFieldsWithMeta) {
      const category = item.field?.category || "Ukjent";
      if (!groups[category]) groups[category] = [];
      groups[category].push(item);
    }
    return groups;
  }, [usedFieldsWithMeta]);

  const handleClick = useCallback(
    (path: string) => {
      const syntax = `[[${path}]]`;
      onInsert(syntax);
      toast({
        title: "Flettekode satt inn",
        description: syntax,
      });
    },
    [onInsert, toast]
  );

  if (usedFieldPaths.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500">
        <Variable className="h-8 w-8 mb-2 opacity-50" />
        <p className="text-sm">Ingen flettekoder i bruk</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Badge variant="secondary">{usedFieldPaths.length}</Badge>
        <span>flettekoder i bruk</span>
      </div>

      {Object.entries(grouped).map(([category, items]) => (
        <div key={category}>
          <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            {category}
          </h4>
          <div className="space-y-2">
            {items.map(({ path, field }) =>
              field ? (
                <MergeFieldCard
                  key={path}
                  field={field}
                  onClick={() => handleClick(path)}
                  showUsageCount={false}
                />
              ) : (
                <button
                  key={path}
                  className="w-full flex items-center justify-between rounded-lg border bg-white p-3 text-left hover:shadow-md hover:border-primary/50 transition-all duration-200 cursor-pointer"
                  onClick={() => handleClick(path)}
                >
                  <code className="text-xs font-mono text-gray-800 bg-gray-100 px-2 py-1 rounded">
                    [[{path}]]
                  </code>
                </button>
              )
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export function MergeFieldPanel({
  onInsert,
  currentContent,
}: MergeFieldPanelProps) {
  return (
    <Tabs defaultValue="fields" className="flex flex-1 flex-col h-full">
      <TabsList className="shrink-0 grid grid-cols-3">
        <TabsTrigger value="fields" className="gap-1 text-xs">
          <Variable className="h-3.5 w-3.5" />
          Felt
        </TabsTrigger>
        <TabsTrigger value="generator" className="gap-1 text-xs">
          <Wand2 className="h-3.5 w-3.5" />
          Generator
        </TabsTrigger>
        <TabsTrigger value="inuse" className="gap-1 text-xs">
          <List className="h-3.5 w-3.5" />
          I bruk
        </TabsTrigger>
      </TabsList>

      <TabsContent value="fields" className="flex-1 overflow-auto mt-3">
        <FieldBrowserTab onInsert={onInsert} />
      </TabsContent>

      <TabsContent value="generator" className="flex-1 overflow-auto mt-3">
        <CodeGenerator onCopy={(code) => onInsert(code)} />
      </TabsContent>

      <TabsContent value="inuse" className="flex-1 overflow-auto mt-3">
        <InUseTab currentContent={currentContent} onInsert={onInsert} />
      </TabsContent>
    </Tabs>
  );
}
