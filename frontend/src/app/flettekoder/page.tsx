"use client";

/**
 * Flettekoder Page - Merge Field Library with Vitec Logic and Layout snippets
 */

import { useState } from "react";
import { ArrowLeft, Variable, GitBranch, Layout, Wand2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FlettekodeLibrary } from "@/components/flettekoder";
import { VitecLogicSection } from "@/components/flettekoder/VitecLogicSection";
import { CodeGenerator } from "@/components/flettekoder/CodeGenerator";

export default function FlettekodePage() {
  const [activeTab, setActiveTab] = useState("variables");

  const handleCopy = (code: string) => {
    // Simple console log for now - toast can be added later
    console.log(`Copied: ${code.slice(0, 30)}${code.length > 30 ? "..." : ""}`);
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="flex items-center gap-4 px-6 py-4 border-b bg-white">
        <Link href="/">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-xl font-semibold">Flettekoder</h1>
          <p className="text-sm text-muted-foreground">
            Søk og kopier Vitec flettekoder og kodemønstre
          </p>
        </div>
      </header>

      {/* Main content with tabs */}
      <main className="flex-1 overflow-hidden flex flex-col">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="flex-1 flex flex-col"
        >
          <div className="border-b px-6 bg-white">
            <TabsList className="h-12">
              <TabsTrigger value="variables" className="gap-2 text-sm">
                <Variable className="h-4 w-4" />
                Variabler
              </TabsTrigger>
              <TabsTrigger value="generator" className="gap-2 text-sm">
                <Wand2 className="h-4 w-4" />
                Kodegenerator
              </TabsTrigger>
              <TabsTrigger value="logic" className="gap-2 text-sm">
                <GitBranch className="h-4 w-4" />
                Vitec Logic
              </TabsTrigger>
              <TabsTrigger value="layout" className="gap-2 text-sm">
                <Layout className="h-4 w-4" />
                Layout
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Variables Tab - Full merge field library */}
          <TabsContent value="variables" className="flex-1 m-0 overflow-hidden">
            <div className="h-full p-6">
              <FlettekodeLibrary
                onCopy={(field) => handleCopy(`[[${field.path}]]`)}
              />
            </div>
          </TabsContent>

          {/* Code Generator Tab */}
          <TabsContent value="generator" className="flex-1 m-0 overflow-auto p-6">
            <CodeGenerator onCopy={handleCopy} />
          </TabsContent>

          {/* Logic & Layout Tab */}
          <TabsContent value="logic" className="flex-1 m-0 overflow-auto p-6">
            <VitecLogicSection onCopy={handleCopy} />
          </TabsContent>

          <TabsContent value="layout" className="flex-1 m-0 overflow-auto p-6">
            <VitecLogicSection onCopy={handleCopy} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
