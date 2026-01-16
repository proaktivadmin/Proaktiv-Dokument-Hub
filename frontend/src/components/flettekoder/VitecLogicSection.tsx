"use client";

/**
 * VitecLogicSection - Displays Vitec Logic patterns and Layout snippets
 * Loads from resources/snippets.json
 */

import { useState, useEffect } from "react";
import { Search, GitBranch, Layout, Code } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CodeSnippetCard, type CodeSnippet } from "./CodeSnippetCard";

interface SnippetCategory {
  category: string;
  items: Array<{
    label: string;
    desc: string;
    code: string;
  }>;
}

interface VitecLogicSectionProps {
  onCopy?: (code: string) => void;
}

export function VitecLogicSection({ onCopy }: VitecLogicSectionProps) {
  const [snippets, setSnippets] = useState<SnippetCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("logic");

  // Load snippets from resources
  useEffect(() => {
    async function loadSnippets() {
      try {
        // In a real app, this would be an API call
        // For now, we'll use a hardcoded version based on snippets.json
        const response = await fetch("/api/snippets");
        if (response.ok) {
          const data = await response.json();
          setSnippets(data);
        } else {
          // Fallback to hardcoded snippets
          setSnippets(FALLBACK_SNIPPETS);
        }
      } catch {
        // Fallback to hardcoded snippets
        setSnippets(FALLBACK_SNIPPETS);
      } finally {
        setIsLoading(false);
      }
    }
    loadSnippets();
  }, []);

  // Filter snippets by category type
  const vitecLogicSnippets = snippets.find(s => s.category === "Vitec Logic")?.items || [];
  const layoutSnippets = snippets.find(s => s.category === "Layout")?.items || [];

  // Filter by search query
  const filterSnippets = (items: CodeSnippet[]) => {
    if (!searchQuery) return items;
    const query = searchQuery.toLowerCase();
    return items.filter(
      item =>
        item.label.toLowerCase().includes(query) ||
        item.desc.toLowerCase().includes(query) ||
        item.code.toLowerCase().includes(query)
    );
  };

  const filteredLogic = filterSnippets(vitecLogicSnippets);
  const filteredLayout = filterSnippets(layoutSnippets);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-500">
        Laster kodeblokker...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          type="search"
          placeholder="Søk i kodeblokker..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="logic" className="gap-2">
            <GitBranch className="h-4 w-4" />
            Vitec Logic ({filteredLogic.length})
          </TabsTrigger>
          <TabsTrigger value="layout" className="gap-2">
            <Layout className="h-4 w-4" />
            Layout ({filteredLayout.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="logic" className="mt-4">
          {filteredLogic.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Ingen Vitec Logic-mønstre funnet
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredLogic.map((item, index) => (
                <CodeSnippetCard
                  key={`logic-${index}`}
                  snippet={item}
                  variant="logic"
                  onCopy={onCopy}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="layout" className="mt-4">
          {filteredLayout.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Ingen Layout-mønstre funnet
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredLayout.map((item, index) => (
                <CodeSnippetCard
                  key={`layout-${index}`}
                  snippet={item}
                  variant="layout"
                  onCopy={onCopy}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Fallback snippets in case API fails
const FALLBACK_SNIPPETS: SnippetCategory[] = [
  {
    category: "Vitec Logic",
    items: [
      {
        label: "If / Else",
        desc: "Betingelsesblokk",
        code: `<vitec:if test="[[variable]]">
    <!-- Vis hvis true -->
<vitec:else />
    <!-- Vis hvis false -->
</vitec:if>`
      },
      {
        label: "Loop List",
        desc: "Iterer over en liste",
        code: `<vitec:foreach items="[[list]]" var="item">
    <p>[[item.name]]</p>
</vitec:foreach>`
      },
      {
        label: "vitec-if (inline)",
        desc: "Inline betingelse på element",
        code: `<span vitec-if="Model.eiendom.pris > 0">
    Pris: [[eiendom.pris]]
</span>`
      },
      {
        label: "vitec-foreach (inline)",
        desc: "Loop på tabellrad",
        code: `<tbody vitec-foreach="selger in Model.selgere">
    <tr>
        <td>[[selger.navn]]</td>
        <td>[[selger.tlf]]</td>
    </tr>
</tbody>`
      },
      {
        label: "Sammenligning",
        desc: "Sjekk mot verdi",
        code: `vitec-if="Model.eiendom.eieform == &quot;Aksje&quot;"`
      },
      {
        label: "Flere betingelser",
        desc: "AND/OR logikk",
        code: `vitec-if="(Model.eiendom.eieform == &quot;Aksje&quot; || Model.eiendom.eieform == &quot;Obligasjonsleilighet&quot;)"`
      }
    ]
  },
  {
    category: "Layout",
    items: [
      {
        label: "2 Kolonner",
        desc: "Grid layout med 2 kolonner",
        code: `<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
    <div>Venstre</div>
    <div>Høyre</div>
</div>`
      },
      {
        label: "Data Tabell",
        desc: "Standard tabell med border",
        code: `<table style="width: 100%; border-collapse: collapse;">
    <tr>
        <th style="border-bottom: 1px solid #000; text-align: left;">Header</th>
        <th style="border-bottom: 1px solid #000; text-align: left;">Verdi</th>
    </tr>
    <tr>
        <td>Data</td>
        <td>Verdi</td>
    </tr>
</table>`
      },
      {
        label: "Signaturblokk",
        desc: "Område for signaturer",
        code: `<div style="display: flex; justify-content: space-between; margin-top: 50px;">
    <div style="text-align: center; width: 45%;">
        <div style="border-top: 1px solid #000; padding-top: 10px;">
            Selgers underskrift
        </div>
    </div>
    <div style="text-align: center; width: 45%;">
        <div style="border-top: 1px solid #000; padding-top: 10px;">
            Meglers underskrift
        </div>
    </div>
</div>`
      },
      {
        label: "Sideskift",
        desc: "Tving ny side i PDF",
        code: `<div style="page-break-before: always;"></div>`
      }
    ]
  }
];
