"use client";

/**
 * SimulatorPanel - Variable detection and test data replacement
 * Parses template content for [[variables]] and allows test value overrides
 * Persists user values to localStorage for reuse across sessions
 */

import { useState, useEffect, useMemo, useCallback } from "react";
import { Play, RefreshCw, Save, Search, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

interface DetectedVariable {
  path: string;
  isRequired: boolean;
  count: number;
}

interface SimulatorPanelProps {
  content: string;
  onApplyTestData?: (processedContent: string) => void;
}

const STORAGE_KEY = "proaktiv_simulator_testdata";

// Default test data - comprehensive set for Norwegian real estate templates
const DEFAULT_TEST_DATA: Record<string, string> = {
  // Dates
  "dagensdato": "15.01.2026",
  // Oppdrag (Assignment)
  "oppdrag.nr": "12-26-0045",
  "oppdrag.provisjonprosent": "1,5%",
  "oppdrag.selgersamletsum": "143 900,-",
  // Selger (Seller)
  "selger.navn": "Ola Nordmann",
  "selger.navnutenfullmektigogkontaktperson": "Ola Nordmann",
  "selger.gatenavnognr": "Solveien 12",
  "selger.hovedgatenavnognr": "Solveien 12",
  "selger.postnr": "0450",
  "selger.hovedpostnr": "0450",
  "selger.poststed": "Oslo",
  "selger.hovedpoststed": "Oslo",
  "selger.emailadresse": "ola.nordmann@test.no",
  "selger.hovedtlf": "900 00 000",
  "selger.tlf": "900 00 000",
  "selger.idnummer": "010180 12345",
  "selger.fdato_orgnr": "01.01.1980",
  "selger.eierbrok": "1/1",
  "selger.adresse": "Solveien 12, 0450 Oslo",
  "selger.ledetekst_fdato_orgnr": "Fødselsdato:",
  // Kjøper (Buyer)
  "kjoper.navn": "Kari Hansen",
  "kjoper.navnutenfullmektigogkontaktperson": "Kari Hansen",
  "kjoper.gatenavnognr": "Strandveien 8",
  "kjoper.postnr": "0250",
  "kjoper.poststed": "Oslo",
  "kjoper.emailadresse": "kari.hansen@test.no",
  "kjoper.tlf": "911 22 333",
  "kjoper.idnummer": "150585 54321",
  "kjoper.fdato_orgnr": "15.05.1985",
  "kjoper.eierbrok": "1/1",
  "kjoper.adresse": "Strandveien 8, 0250 Oslo",
  "kjoper.ledetekst_fdato_orgnr": "Fødselsdato:",
  // Meglerkontor (Broker Office)
  "meglerkontor.navn": "Proaktiv Eiendomsmegling AS",
  "meglerkontor.markedsforingsnavn": "Proaktiv Majorstuen",
  "meglerkontor.juridisknavn": "Proaktiv Eiendomsmegling AS",
  "meglerkontor.kjedenavn": "Proaktiv",
  "meglerkontor.besoksadresse": "Bogstadveien 1",
  "meglerkontor.besokspostnr": "0355",
  "meglerkontor.besokspoststed": "Oslo",
  "meglerkontor.adresse": "Postboks 123",
  "meglerkontor.postnr": "0355",
  "meglerkontor.poststed": "Oslo",
  "meglerkontor.orgnr": "987 654 321 MVA",
  "meglerkontor.tlf": "22 22 22 22",
  "meglerkontor.epost": "majorstuen@proaktiv.no",
  "meglerkontor.firmalogourl": "/assets/proaktiv-logo-black.png",
  "meglerkontor.fullmektigenavn": "Per Fullmektig",
  // Ansvarlig megler (Responsible Broker)
  "ansvarligmegler.navn": "Ansvarlig Meglersen",
  "ansvarligmegler.tittel": "Fagansvarlig / Eiendomsmegler MNEF",
  "ansvarligmegler.epost": "ansvarlig@proaktiv.no",
  // Megler2 (Second Broker)
  "megler2.navn": "Medarbeider Meglersen",
  "megler2.tittel": "Eiendomsmegler",
  // Oppgjør (Settlement)
  "oppgjor.kontornavn": "Proaktiv Oppgjør",
  "oppgjor.besoksadresse": "Bogstadveien 1",
  "oppgjor.kontorepost": "oppgjor@proaktiv.no",
  "oppgjor.kontortlf": "22 22 22 23",
  "oppgjor.orgnr": "987 654 322 MVA",
  // Eiendom (Property)
  "eiendom.boligtype": "Selveierleilighet",
  "eiendom.gatenavnognr": "Storgata 5B",
  "eiendom.adresse": "Storgata 5B",
  "eiendom.postnr": "0150",
  "eiendom.poststed": "Oslo",
  "eiendom.kommunenavn": "Oslo",
  "eiendom.pris": "4 500 000,-",
  "eiendom.bruksareal": "75 m²",
  "eiendom.bruttoareal": "82 m²",
  "eiendom.fellesgjeld": "250 000,-",
  "eiendom.andelsnr": "42",
  "eiendom.tomtetype": "Fellestomt",
  "eiendom.takstdato": "10.01.2026",
  "eiendom.nestevisning.formaterttekst": "Søndag 19. januar kl. 12:00-13:00",
  // Matrikkel
  "komplettmatrikkelutvidet": "Gnr. 45 Bnr. 2 Snr. 9 i Oslo kommune",
};

// Load saved test data from localStorage
function loadSavedTestData(): Record<string, string> {
  if (typeof window === "undefined") return {};
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : {};
  } catch {
    return {};
  }
}

// Save test data to localStorage
function saveTestData(data: Record<string, string>) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (e) {
    console.error("Failed to save test data:", e);
  }
}

export function SimulatorPanel({ content, onApplyTestData }: SimulatorPanelProps) {
  const [testValues, setTestValues] = useState<Record<string, string>>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  // Detect all [[variables]] in content
  const detectedVariables = useMemo((): DetectedVariable[] => {
    if (!content) return [];
    
    const regex = /\[\[(\*?)([^\]]+)\]\]/g;
    const variables = new Map<string, DetectedVariable>();
    
    let match;
    while ((match = regex.exec(content)) !== null) {
      const isRequired = match[1] === "*";
      const path = match[2].trim();
      
      const existing = variables.get(path);
      if (existing) {
        existing.count++;
        if (isRequired) existing.isRequired = true;
      } else {
        variables.set(path, {
          path,
          isRequired,
          count: 1,
        });
      }
    }
    
    return Array.from(variables.values()).sort((a, b) => 
      a.path.localeCompare(b.path)
    );
  }, [content]);

  // Initialize test values: First from localStorage, then fill gaps from defaults
  useEffect(() => {
    const savedData = loadSavedTestData();
    const initial: Record<string, string> = {};
    
    detectedVariables.forEach((v) => {
      // Priority: 1) Saved value, 2) Default value
      if (savedData[v.path]) {
        initial[v.path] = savedData[v.path];
      } else {
        const defaultValue = DEFAULT_TEST_DATA[v.path] || DEFAULT_TEST_DATA[`*${v.path}`];
        if (defaultValue) {
          initial[v.path] = defaultValue;
        }
      }
    });
    setTestValues(initial);
  }, [detectedVariables]);

  // Filter variables by search
  const filteredVariables = useMemo(() => {
    if (!searchQuery) return detectedVariables;
    const query = searchQuery.toLowerCase();
    return detectedVariables.filter((v) =>
      v.path.toLowerCase().includes(query)
    );
  }, [detectedVariables, searchQuery]);

  // Count variables with/without values
  const stats = useMemo(() => {
    const withValues = detectedVariables.filter((v) => testValues[v.path]).length;
    const required = detectedVariables.filter((v) => v.isRequired).length;
    const missingRequired = detectedVariables.filter(
      (v) => v.isRequired && !testValues[v.path]
    ).length;
    return { total: detectedVariables.length, withValues, required, missingRequired };
  }, [detectedVariables, testValues]);

  const handleValueChange = (path: string, value: string) => {
    setTestValues((prev) => ({
      ...prev,
      [path]: value,
    }));
  };

  const handleApplyTestData = () => {
    if (!onApplyTestData) return;
    
    setIsLoading(true);
    try {
      // Replace all [[variables]] with test values
      let processedContent = content;
      
      detectedVariables.forEach((variable) => {
        const value = testValues[variable.path] || `[[${variable.path}]]`;
        // Replace both [[path]] and [[*path]] variants
        processedContent = processedContent.replace(
          new RegExp(`\\[\\[\\*?${escapeRegExp(variable.path)}\\]\\]`, "g"),
          value
        );
      });
      
      onApplyTestData(processedContent);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetToDefaults = () => {
    const initial: Record<string, string> = {};
    detectedVariables.forEach((v) => {
      const defaultValue = DEFAULT_TEST_DATA[v.path] || DEFAULT_TEST_DATA[`*${v.path}`];
      if (defaultValue) {
        initial[v.path] = defaultValue;
      }
    });
    setTestValues(initial);
  };

  const handleClearAll = () => {
    setTestValues({});
  };

  const handleSaveAsDefault = useCallback(() => {
    // Save current values merged with existing saved data
    const existingSaved = loadSavedTestData();
    const merged = { ...existingSaved, ...testValues };
    saveTestData(merged);
    setSaveMessage("Lagret som standard!");
    setTimeout(() => setSaveMessage(null), 2000);
  }, [testValues]);

  if (!content) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Ingen innhold å simulere</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Stats bar */}
      <div className="flex items-center justify-between gap-4 p-4 border-b bg-gray-50">
        <div className="flex items-center gap-2 text-sm">
          <Badge variant="outline">{stats.total} variabler</Badge>
          <Badge variant="secondary">{stats.withValues} med verdi</Badge>
          {stats.missingRequired > 0 && (
            <Badge variant="destructive">{stats.missingRequired} påkrevd mangler</Badge>
          )}
          {saveMessage && (
            <span className="text-green-600 text-xs font-medium animate-pulse">
              ✓ {saveMessage}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleSaveAsDefault} title="Lagre verdier som standard for fremtidige maler">
            <Save className="h-4 w-4 mr-1" />
            Lagre
          </Button>
          <Button variant="outline" size="sm" onClick={handleResetToDefaults}>
            <RefreshCw className="h-4 w-4 mr-1" />
            Standard
          </Button>
          <Button variant="outline" size="sm" onClick={handleClearAll}>
            Tøm alle
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="p-4 border-b">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="search"
            placeholder="Søk variabler..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Variable list */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {filteredVariables.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {searchQuery ? "Ingen variabler matcher søket" : "Ingen variabler funnet i malen"}
            </div>
          ) : (
            filteredVariables.map((variable) => (
              <div key={variable.path} className="space-y-1">
                <div className="flex items-center gap-2">
                  <Label
                    htmlFor={`var-${variable.path}`}
                    className="text-sm font-mono text-gray-600"
                  >
                    [[{variable.path}]]
                  </Label>
                  {variable.isRequired && (
                    <Badge variant="outline" className="text-xs text-red-600 border-red-300">
                      Påkrevd
                    </Badge>
                  )}
                  {variable.count > 1 && (
                    <span className="text-xs text-gray-400">({variable.count}x)</span>
                  )}
                </div>
                <Input
                  id={`var-${variable.path}`}
                  value={testValues[variable.path] || ""}
                  onChange={(e) => handleValueChange(variable.path, e.target.value)}
                  placeholder={DEFAULT_TEST_DATA[variable.path] || "Skriv testverdi..."}
                  className="font-mono text-sm"
                />
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      <Separator />

      {/* Apply button */}
      <div className="p-4">
        <Button
          onClick={handleApplyTestData}
          disabled={isLoading || !onApplyTestData}
          className="w-full"
        >
          <Play className="h-4 w-4 mr-2" />
          {isLoading ? "Behandler..." : "Forhåndsvis med testdata"}
        </Button>
      </div>
    </div>
  );
}

// Helper function to escape special regex characters
function escapeRegExp(string: string): string {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
