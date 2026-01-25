"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Upload, FileText, FolderTree, LayoutDashboard, Sparkles, Code2, HardDrive, LogOut,
  Building2, Users, Image, ChevronDown, FileCode, Plus, Map, RefreshCcw, Palette, ClipboardList
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { UploadTemplateDialog } from "@/components/templates/UploadTemplateDialog";
import { NewTemplateDialog } from "@/components/templates/NewTemplateDialog";
import { NotificationDropdown } from "@/components/notifications/NotificationDropdown";
import { cn } from "@/lib/utils";
import { authApi } from "@/lib/api/auth";

interface HeaderProps {
  onUploadSuccess?: () => void;
}

export function Header({ onUploadSuccess }: HeaderProps) {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [newTemplateDialogOpen, setNewTemplateDialogOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  // Scroll shadow effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleUploadSuccess = () => {
    setUploadDialogOpen(false);
    onUploadSuccess?.();
  };

  const handleNewTemplateSuccess = () => {
    setNewTemplateDialogOpen(false);
    onUploadSuccess?.();
  };

  const handleLogout = async () => {
    await authApi.logout();
    router.push("/login");
    router.refresh();
  };

  const navItems = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/flettekoder", label: "Flettekoder", icon: Code2 },
  ];

  // Ressurser - all files, documents, assets
  const ressurserItems = [
    { href: "/templates", label: "Maler", icon: FileText },
    { href: "/categories", label: "Kategorier", icon: FolderTree },
    { href: "/assets", label: "Mediefiler", icon: Image },
    { href: "/storage", label: "WebDAV Lagring", icon: HardDrive },
  ];

  // Selskap - HR/organization
  const selskapItems = [
    { href: "/offices", label: "Kontorer", icon: Building2 },
    { href: "/employees", label: "Ansatte", icon: Users },
    { href: "/territories", label: "Markedsområder", icon: Map },
    { href: "/mottakere", label: "Mottakere", icon: Users },
  ];

  // Tools dropdown items
  const toolsItems = [
    { href: "/tools/office-overview", label: "Kontor-oversikt", icon: ClipboardList },
    { href: "/sanitizer", label: "Sanitizer", icon: Sparkles },
    { href: "/sync", label: "Synkronisering", icon: RefreshCcw },
    { href: "/portal/preview", label: "Portal Skins", icon: Palette },
    { href: "/tools/image-optimizer", label: "Bildeoptimalisering", icon: Image },
  ];

  const isRessurserActive = ["/templates", "/categories", "/assets", "/storage"].some(p => pathname.startsWith(p));
  const isSelskapActive = ["/offices", "/employees", "/territories", "/mottakere"].some(p => pathname.startsWith(p));
  const isToolsActive = ["/sanitizer", "/sync", "/portal", "/tools"].some(p => pathname.startsWith(p));

  return (
    <>
      <header className={cn(
        "border-b border-[#E5E5E5] bg-[#E9E7DC] sticky top-0 z-50 transition-shadow duration-normal",
        isScrolled && "shadow-medium"
      )}>
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center">
              <img
                src="https://proaktiv.no/assets/logos/logo.svg"
                alt="Proaktiv"
                className="h-8 w-auto"
              />
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

              {/* Ressurser Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    className={cn(
                      "px-4 py-2 text-sm font-medium rounded-md transition-colors inline-flex items-center gap-2 group",
                      isRessurserActive
                        ? "bg-white/60 text-[#272630]"
                        : "text-[#272630]/70 hover:text-[#272630] hover:bg-white/40"
                    )}
                  >
                    <FolderTree className="h-4 w-4" />
                    Ressurser
                    <ChevronDown className="h-3 w-3 transition-transform duration-fast ease-standard group-data-[state=open]:rotate-180" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48 bg-white">
                  {ressurserItems.map((item) => {
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

              {/* Selskap Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    className={cn(
                      "px-4 py-2 text-sm font-medium rounded-md transition-colors inline-flex items-center gap-2 group",
                      isSelskapActive
                        ? "bg-white/60 text-[#272630]"
                        : "text-[#272630]/70 hover:text-[#272630] hover:bg-white/40"
                    )}
                  >
                    <Building2 className="h-4 w-4" />
                    Selskap
                    <ChevronDown className="h-3 w-3 transition-transform duration-fast ease-standard group-data-[state=open]:rotate-180" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48 bg-white">
                  {selskapItems.map((item) => {
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
                      "px-4 py-2 text-sm font-medium rounded-md transition-colors inline-flex items-center gap-2 group",
                      isToolsActive
                        ? "bg-white/60 text-[#272630]"
                        : "text-[#272630]/70 hover:text-[#272630] hover:bg-white/40"
                    )}
                  >
                    <Sparkles className="h-4 w-4" />
                    Verktøy
                    <ChevronDown className="h-3 w-3 transition-transform duration-fast ease-standard group-data-[state=open]:rotate-180" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48 bg-white">
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

              {/* New Template Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button className="ml-3 bg-[#272630] text-white hover:bg-[#272630]/90 rounded-md group">
                    <Plus className="h-4 w-4 mr-2" />
                    Ny mal
                    <ChevronDown className="h-3 w-3 ml-2 transition-transform duration-fast ease-standard group-data-[state=open]:rotate-180" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48 bg-white">
                  <DropdownMenuItem onClick={() => setUploadDialogOpen(true)}>
                    <Upload className="h-4 w-4 mr-2" />
                    Last opp fil
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setNewTemplateDialogOpen(true)}>
                    <FileCode className="h-4 w-4 mr-2" />
                    Lim inn HTML
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Notification Dropdown */}
              <NotificationDropdown className="ml-2" />

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

      <NewTemplateDialog
        open={newTemplateDialogOpen}
        onOpenChange={setNewTemplateDialogOpen}
        onSuccess={handleNewTemplateSuccess}
      />
    </>
  );
}
