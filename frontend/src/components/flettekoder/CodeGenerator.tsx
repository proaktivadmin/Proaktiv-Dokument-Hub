"use client";

/**
 * CodeGenerator - Interactive tool for building Vitec code snippets
 * Allows non-technical users to create if/else conditions, loops, and comparisons
 */

import { useState, useMemo } from "react";
import { Copy, Check, Plus, Trash2, Code, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useMergeFields } from "@/hooks/v2/useMergeFields";

// ConditionType is reserved for future complex condition builder
// type ConditionType = "simple" | "comparison" | "multiple";
type Operator = "==" | "!=" | ">" | "<" | ">=" | "<=";
type LogicOperator = "&&" | "||";

interface Condition {
  id: string;
  field: string;
  operator: Operator;
  value: string;
  logicOperator?: LogicOperator;
}

interface CodeGeneratorProps {
  onCopy?: (code: string) => void;
}

export function CodeGenerator({ onCopy }: CodeGeneratorProps) {
  const { fields: mergeFields = [] } = useMergeFields({ perPage: 200 });
  const [copied, setCopied] = useState(false);
  const [activeGenerator, setActiveGenerator] = useState<"if" | "foreach" | "inline">("if");
  
  // If/Else state
  const [conditions, setConditions] = useState<Condition[]>([
    { id: "1", field: "", operator: "==", value: "" }
  ]);
  const [trueContent, setTrueContent] = useState("<!-- Vis dette hvis betingelsen er sann -->");
  const [falseContent, setFalseContent] = useState("<!-- Vis dette hvis betingelsen er usann -->");
  const [includeFalse, setIncludeFalse] = useState(false);
  
  // Foreach state
  const [listField, setListField] = useState("");
  const [itemName, setItemName] = useState("item");
  const [loopContent, setLoopContent] = useState("<p>[[item.navn]]</p>");
  
  // Inline if state
  const [inlineField, setInlineField] = useState("");
  const [inlineOperator, setInlineOperator] = useState<Operator>(">");
  const [inlineValue, setInlineValue] = useState("0");
  const [inlineElement, setInlineElement] = useState("span");
  const [inlineContent, setInlineContent] = useState("[[eiendom.pris]]");

  // Available fields for dropdown
  const fieldOptions = useMemo(() => {
    return mergeFields.map(f => ({
      value: f.path,
      label: f.label || f.path,
      category: f.category
    }));
  }, [mergeFields]);

  // Iterable fields for foreach
  const iterableFields = useMemo(() => {
    return mergeFields.filter(f => f.is_iterable).map(f => ({
      value: f.path,
      label: f.label || f.path
    }));
  }, [mergeFields]);

  // Generate if/else code
  const generatedIfCode = useMemo(() => {
    const validConditions = conditions.filter(c => c.field);
    if (validConditions.length === 0) {
      return "<!-- Velg et felt for å generere kode -->";
    }

    let conditionStr: string;
    if (validConditions.length === 1) {
      const c = validConditions[0];
      conditionStr = `Model.${c.field} ${c.operator} &quot;${c.value}&quot;`;
    } else {
      const parts = validConditions.map((c, i) => {
        const part = `Model.${c.field} ${c.operator} &quot;${c.value}&quot;`;
        if (i === 0) return part;
        return `${c.logicOperator === "||" ? "||" : "&&"} ${part}`;
      });
      conditionStr = `(${parts.join(" ")})`;
    }

    let code = `<div vitec-if="${conditionStr}">\n    ${trueContent}\n</div>`;
    
    if (includeFalse) {
      code = `<vitec:if test="${conditionStr}">
    ${trueContent}
<vitec:else />
    ${falseContent}
</vitec:if>`;
    }
    
    return code;
  }, [conditions, trueContent, falseContent, includeFalse]);

  // Generate foreach code
  const generatedForeachCode = useMemo(() => {
    if (!listField) {
      return "<!-- Velg en liste for å generere kode -->";
    }
    
    return `<tbody vitec-foreach="${itemName} in Model.${listField}">
    <tr>
        ${loopContent}
    </tr>
</tbody>`;
  }, [listField, itemName, loopContent]);

  // Generate inline if code
  const generatedInlineCode = useMemo(() => {
    if (!inlineField) {
      return "<!-- Velg et felt for å generere kode -->";
    }
    
    return `<${inlineElement} vitec-if="Model.${inlineField} ${inlineOperator} ${inlineValue}">
    ${inlineContent}
</${inlineElement}>`;
  }, [inlineField, inlineOperator, inlineValue, inlineElement, inlineContent]);

  // Get current generated code based on active tab
  const currentCode = activeGenerator === "if" 
    ? generatedIfCode 
    : activeGenerator === "foreach" 
      ? generatedForeachCode 
      : generatedInlineCode;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(currentCode);
    setCopied(true);
    onCopy?.(currentCode);
    setTimeout(() => setCopied(false), 2000);
  };

  const addCondition = () => {
    setConditions([
      ...conditions,
      { id: String(Date.now()), field: "", operator: "==", value: "", logicOperator: "&&" }
    ]);
  };

  const removeCondition = (id: string) => {
    if (conditions.length > 1) {
      setConditions(conditions.filter(c => c.id !== id));
    }
  };

  const updateCondition = (id: string, updates: Partial<Condition>) => {
    setConditions(conditions.map(c => c.id === id ? { ...c, ...updates } : c));
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-full">
      {/* Generator Panel */}
      <div className="flex-1 space-y-4">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Wand2 className="h-5 w-5 text-primary" />
              <CardTitle>Kodegenerator</CardTitle>
            </div>
            <CardDescription>
              Bygg Vitec-kode uten å skrive kode. Velg felter og betingelser, så genereres HTML-koden automatisk.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={activeGenerator} onValueChange={(v) => setActiveGenerator(v as typeof activeGenerator)}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="if">If / Else</TabsTrigger>
                <TabsTrigger value="foreach">Loop (foreach)</TabsTrigger>
                <TabsTrigger value="inline">Inline If</TabsTrigger>
              </TabsList>

              {/* If/Else Generator */}
              <TabsContent value="if" className="space-y-4 mt-4">
                <div className="space-y-3">
                  <Label className="font-medium">Betingelser</Label>
                  {conditions.map((condition, index) => (
                    <div key={condition.id} className="flex items-center gap-2">
                      {index > 0 && (
                        <Select
                          value={condition.logicOperator || "&&"}
                          onValueChange={(v) => updateCondition(condition.id, { logicOperator: v as LogicOperator })}
                        >
                          <SelectTrigger className="w-20">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="&&">OG</SelectItem>
                            <SelectItem value="||">ELLER</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                      <Select
                        value={condition.field}
                        onValueChange={(v) => updateCondition(condition.id, { field: v })}
                      >
                        <SelectTrigger className="flex-1">
                          <SelectValue placeholder="Velg felt..." />
                        </SelectTrigger>
                        <SelectContent>
                          {fieldOptions.map((f) => (
                            <SelectItem key={f.value} value={f.value}>
                              {f.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Select
                        value={condition.operator}
                        onValueChange={(v) => updateCondition(condition.id, { operator: v as Operator })}
                      >
                        <SelectTrigger className="w-24">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="==">er lik</SelectItem>
                          <SelectItem value="!=">er ikke</SelectItem>
                          <SelectItem value=">">større enn</SelectItem>
                          <SelectItem value="<">mindre enn</SelectItem>
                          <SelectItem value=">=">≥</SelectItem>
                          <SelectItem value="<=">≤</SelectItem>
                        </SelectContent>
                      </Select>
                      <Input
                        placeholder="Verdi..."
                        value={condition.value}
                        onChange={(e) => updateCondition(condition.id, { value: e.target.value })}
                        className="w-40"
                      />
                      {conditions.length > 1 && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeCondition(condition.id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      )}
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addCondition}>
                    <Plus className="h-4 w-4 mr-1" /> Legg til betingelse
                  </Button>
                </div>

                <div className="space-y-2">
                  <Label>Innhold hvis sant</Label>
                  <Textarea
                    value={trueContent}
                    onChange={(e) => setTrueContent(e.target.value)}
                    placeholder="HTML-innhold..."
                    rows={2}
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="include-false"
                    checked={includeFalse}
                    onChange={(e) => setIncludeFalse(e.target.checked)}
                    className="h-4 w-4"
                  />
                  <Label htmlFor="include-false">Inkluder else-blokk</Label>
                </div>

                {includeFalse && (
                  <div className="space-y-2">
                    <Label>Innhold hvis usant</Label>
                    <Textarea
                      value={falseContent}
                      onChange={(e) => setFalseContent(e.target.value)}
                      placeholder="HTML-innhold..."
                      rows={2}
                    />
                  </div>
                )}
              </TabsContent>

              {/* Foreach Generator */}
              <TabsContent value="foreach" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label>Liste å loope over</Label>
                  <Select value={listField} onValueChange={setListField}>
                    <SelectTrigger>
                      <SelectValue placeholder="Velg en liste..." />
                    </SelectTrigger>
                    <SelectContent>
                      {iterableFields.length > 0 ? (
                        iterableFields.map((f) => (
                          <SelectItem key={f.value} value={f.value}>
                            {f.label}
                          </SelectItem>
                        ))
                      ) : (
                        <>
                          <SelectItem value="selgere">selgere (liste)</SelectItem>
                          <SelectItem value="kjopere">kjopere (liste)</SelectItem>
                          <SelectItem value="dokumenter">dokumenter (liste)</SelectItem>
                          <SelectItem value="bilder">bilder (liste)</SelectItem>
                        </>
                      )}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Variabelnavn for hvert element</Label>
                  <Input
                    value={itemName}
                    onChange={(e) => setItemName(e.target.value)}
                    placeholder="f.eks. selger, kjoper, item"
                  />
                  <p className="text-xs text-muted-foreground">
                    Du kan bruke [[{itemName}.felt]] i loop-innholdet
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>Innhold per element</Label>
                  <Textarea
                    value={loopContent}
                    onChange={(e) => setLoopContent(e.target.value)}
                    placeholder={`<td>[[${itemName}.navn]]</td>`}
                    rows={3}
                  />
                </div>
              </TabsContent>

              {/* Inline If Generator */}
              <TabsContent value="inline" className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>HTML-element</Label>
                    <Select value={inlineElement} onValueChange={setInlineElement}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="span">span</SelectItem>
                        <SelectItem value="div">div</SelectItem>
                        <SelectItem value="p">p (avsnitt)</SelectItem>
                        <SelectItem value="tr">tr (tabellrad)</SelectItem>
                        <SelectItem value="td">td (tabellcelle)</SelectItem>
                        <SelectItem value="li">li (listeelement)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Felt å sjekke</Label>
                    <Select value={inlineField} onValueChange={setInlineField}>
                      <SelectTrigger>
                        <SelectValue placeholder="Velg felt..." />
                      </SelectTrigger>
                      <SelectContent>
                        {fieldOptions.map((f) => (
                          <SelectItem key={f.value} value={f.value}>
                            {f.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Operator</Label>
                    <Select value={inlineOperator} onValueChange={(v) => setInlineOperator(v as Operator)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value=">">større enn (&gt;)</SelectItem>
                        <SelectItem value="<">mindre enn (&lt;)</SelectItem>
                        <SelectItem value="==">er lik (==)</SelectItem>
                        <SelectItem value="!=">er ikke (!=)</SelectItem>
                        <SelectItem value=">=">større eller lik (≥)</SelectItem>
                        <SelectItem value="<=">mindre eller lik (≤)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Verdi</Label>
                    <Input
                      value={inlineValue}
                      onChange={(e) => setInlineValue(e.target.value)}
                      placeholder="0, 'tekst', etc."
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Innhold å vise</Label>
                  <Textarea
                    value={inlineContent}
                    onChange={(e) => setInlineContent(e.target.value)}
                    placeholder="Pris: [[eiendom.pris]]"
                    rows={2}
                  />
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      {/* Preview Panel */}
      <div className="lg:w-96 space-y-4">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Code className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">Generert kode</CardTitle>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopy}
                disabled={currentCode.includes("Velg")}
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4 mr-1 text-green-500" />
                    Kopiert!
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4 mr-1" />
                    Kopier
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg text-sm overflow-x-auto whitespace-pre-wrap font-mono">
              {currentCode}
            </pre>
            {!currentCode.includes("Velg") && (
              <div className="mt-3 flex gap-2">
                <Badge variant="secondary" className="text-xs">
                  {activeGenerator === "if" ? "vitec-if" : activeGenerator === "foreach" ? "vitec-foreach" : "inline"}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Klar til bruk
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-4">
            <h4 className="font-medium text-blue-900 mb-2">💡 Tips</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Bruk <code className="bg-blue-100 px-1 rounded">[[felt.navn]]</code> for å sette inn verdier</li>
              <li>• Kombiner flere betingelser med OG/ELLER</li>
              <li>• Inline-if er best for enkle sjekker</li>
              <li>• Foreach brukes for lister som selgere/kjøpere</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
