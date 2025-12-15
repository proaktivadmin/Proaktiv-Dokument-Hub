"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Upload, FileText, FolderTree, LayoutDashboard } from "lucide-react";
import { Button } from "@/components/ui/button";
import { UploadTemplateDialog } from "@/components/templates/UploadTemplateDialog";
import { cn } from "@/lib/utils";

interface HeaderProps {
  onUploadSuccess?: () => void;
}

export function Header({ onUploadSuccess }: HeaderProps) {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const pathname = usePathname();

  const handleUploadSuccess = () => {
    setUploadDialogOpen(false);
    onUploadSuccess?.();
  };

  const navItems = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/templates", label: "Maler", icon: FileText },
    { href: "/categories", label: "Kategorier", icon: FolderTree },
  ];

  return (
    <>
      <header className="border-b border-[#E5E5E5] bg-[#E9E7DC] sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-md bg-[#272630] flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-[#272630]">
                  Proaktiv Dokument Hub
                </h1>
                <p className="text-sm text-[#272630]/60">Master Template Library</p>
              </div>
            </Link>

            <nav className="flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "px-4 py-2 text-sm font-medium rounded-md transition-colors inline-flex items-center gap-2",
                      isActive
                        ? "bg-white/60 text-[#272630]"
                        : "text-[#272630]/70 hover:text-[#272630] hover:bg-white/40"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                );
              })}

              <Button
                onClick={() => setUploadDialogOpen(true)}
                className="ml-3 bg-[#272630] text-white hover:bg-[#272630]/90 rounded-md"
              >
                <Upload className="h-4 w-4 mr-2" />
                Last opp
              </Button>
            </nav>
          </div>
        </div>
      </header>

      <UploadTemplateDialog
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
        onSuccess={handleUploadSuccess}
      />
    </>
  );
}
