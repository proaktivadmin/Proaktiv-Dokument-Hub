"use client";

import { Header } from "@/components/layout/Header";
import { DeduplicationDashboard } from "@/components/editor/DeduplicationDashboard";
import { Merge } from "lucide-react";

export default function DedupPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center gap-3 mb-8">
          <Merge className="h-7 w-7 text-[#BCAB8A]" />
          <div>
            <h2 className="text-2xl font-serif font-bold text-[#272630]">Deduplisering</h2>
            <p className="text-[#272630]/60 font-sans">
              Identifiser og slå sammen maler som dekker samme formål
            </p>
          </div>
        </div>

        <DeduplicationDashboard />
      </main>
    </div>
  );
}
