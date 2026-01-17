"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  Upload, FileText, FolderTree, LayoutDashboard, Sparkles, Code2, HardDrive, LogOut,
  Building2, Users, Image, ChevronDown
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { UploadTemplateDialog } from "@/components/templates/UploadTemplateDialog";
import { cn } from "@/lib/utils";
import { authApi } from "@/lib/api/auth";

interface HeaderProps {
  onUploadSuccess?: () => void;
}

export function Header({ onUploadSuccess }: HeaderProps) {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  const handleUploadSuccess = () => {
    setUploadDialogOpen(false);
    onUploadSuccess?.();
  };

  const handleLogout = async () => {
    await authApi.logout();
    router.push("/login");
    router.refresh();
  };

  const navItems = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/templates", label: "Maler", icon: FileText },
    { href: "/flettekoder", label: "Flettekoder", icon: Code2 },
  ];

  // Company Hub dropdown items
  const companyHubItems = [
    { href: "/offices", label: "Kontorer", icon: Building2 },
    { href: "/employees", label: "Ansatte", icon: Users },
    { href: "/assets", label: "Mediefiler", icon: Image },
  ];

  // Tools dropdown items
  const toolsItems = [
    { href: "/categories", label: "Kategorier", icon: FolderTree },
    { href: "/storage", label: "WebDAV Lagring", icon: HardDrive },
    { href: "/sanitizer", label: "Sanitizer", icon: Sparkles },
  ];

  const isCompanyHubActive = ["/offices", "/employees", "/assets"].some(p => pathname.startsWith(p));
  const isToolsActive = ["/categories", "/storage", "/sanitizer"].some(p => pathname.startsWith(p));

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

              {/* Company Hub Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    className={cn(
                      "px-4 py-2 text-sm font-medium rounded-md transition-colors inline-flex items-center gap-2",
                      isCompanyHubActive
                        ? "bg-white/60 text-[#272630]"
                        : "text-[#272630]/70 hover:text-[#272630] hover:bg-white/40"
                    )}
                  >
                    <Building2 className="h-4 w-4" />
                    Selskap
                    <ChevronDown className="h-3 w-3" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48">
                  {companyHubItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <DropdownMenuItem key={item.href} asChild>
                        <Link href={item.href} className="flex items-center gap-2">
                          <Icon className="h-4 w-4" />
                          {item.label}
                        </Link>
                      </DropdownMenuItem>
                    );
                  })}
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Tools Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    className={cn(
                      "px-4 py-2 text-sm font-medium rounded-md transition-colors inline-flex items-center gap-2",
                      isToolsActive
                        ? "bg-white/60 text-[#272630]"
                        : "text-[#272630]/70 hover:text-[#272630] hover:bg-white/40"
                    )}
                  >
                    <Sparkles className="h-4 w-4" />
                    Verktøy
                    <ChevronDown className="h-3 w-3" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48">
                  {toolsItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <DropdownMenuItem key={item.href} asChild>
                        <Link href={item.href} className="flex items-center gap-2">
                          <Icon className="h-4 w-4" />
                          {item.label}
                        </Link>
                      </DropdownMenuItem>
                    );
                  })}
                </DropdownMenuContent>
              </DropdownMenu>

              <Button
                onClick={() => setUploadDialogOpen(true)}
                className="ml-3 bg-[#272630] text-white hover:bg-[#272630]/90 rounded-md"
              >
                <Upload className="h-4 w-4 mr-2" />
                Last opp
              </Button>

              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                className="ml-2 text-[#272630]/70 hover:text-[#272630] hover:bg-white/40"
                title="Logg ut"
              >
                <LogOut className="h-4 w-4" />
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
