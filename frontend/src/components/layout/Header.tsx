"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Upload, FileText, FolderTree, LayoutDashboard, Sparkles, Code2, HardDrive, LogOut,
  Building2, Users, Image, ChevronDown, FileCode, Plus, Map, RefreshCcw, Palette, ClipboardList, BarChart3,
  Sun, Moon
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
import { Switch } from "@/components/ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useTheme } from "@/components/theme/ThemeContext";
import { cn } from "@/lib/utils";
import { authApi } from "@/lib/api/auth";

interface HeaderProps {
  onUploadSuccess?: () => void;
}

export function Header({ onUploadSuccess }: HeaderProps) {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [newTemplateDialogOpen, setNewTemplateDialogOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const pathname = usePathname();
  const router = useRouter();
  const { isDark, setDark } = useTheme();

  // Scroll shadow effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Fetch current user
  useEffect(() => {
    authApi.getStatus().then((status) => {
      if (status.authenticated && status.email) {
        setUserEmail(status.email);
      }
    }).catch(() => {});
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
    { href: "/reports", label: "Formidlingsrapport", icon: BarChart3 },
    { href: "/tools/office-overview", label: "Kontor-oversikt", icon: ClipboardList },
    { href: "/sanitizer", label: "Sanitizer", icon: Sparkles },
    { href: "/sync", label: "Synkronisering", icon: RefreshCcw },
    { href: "/portal/preview", label: "Portal Skins", icon: Palette },
    { href: "/tools/image-optimizer", label: "Bildeoptimalisering", icon: Image },
  ];

  const isRessurserActive = ["/templates", "/categories", "/assets", "/storage"].some(p => pathname.startsWith(p));
  const isSelskapActive = ["/offices", "/employees", "/territories", "/mottakere"].some(p => pathname.startsWith(p));
  const isToolsActive = ["/sanitizer", "/sync", "/portal", "/tools", "/reports"].some(p => pathname.startsWith(p));

  return (
    <>
      <header className={cn(
        "border-b border-border bg-secondary sticky top-0 z-100 transition-shadow duration-normal",
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
                        ? "bg-card/60 text-foreground dark:bg-card/40"
                        : "text-muted-foreground hover:text-foreground hover:bg-card/40 dark:hover:bg-card/30"
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
                        ? "bg-card/60 text-foreground dark:bg-card/40"
                        : "text-muted-foreground hover:text-foreground hover:bg-card/40 dark:hover:bg-card/30"
                    )}
                  >
                    <FolderTree className="h-4 w-4" />
                    Ressurser
                    <ChevronDown className="h-3 w-3 transition-transform duration-fast ease-standard group-data-[state=open]:rotate-180" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48 bg-card">
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
                        ? "bg-card/60 text-foreground dark:bg-card/40"
                        : "text-muted-foreground hover:text-foreground hover:bg-card/40 dark:hover:bg-card/30"
                    )}
                  >
                    <Building2 className="h-4 w-4" />
                    Selskap
                    <ChevronDown className="h-3 w-3 transition-transform duration-fast ease-standard group-data-[state=open]:rotate-180" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48 bg-card">
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
                        ? "bg-card/60 text-foreground dark:bg-card/40"
                        : "text-muted-foreground hover:text-foreground hover:bg-card/40 dark:hover:bg-card/30"
                    )}
                  >
                    <Sparkles className="h-4 w-4" />
                    Verktøy
                    <ChevronDown className="h-3 w-3 transition-transform duration-fast ease-standard group-data-[state=open]:rotate-180" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48 bg-card">
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
                  <Button className="ml-3 bg-primary text-primary-foreground hover:bg-primary/90 rounded-md group">
                    <Plus className="h-4 w-4 mr-2" />
                    Ny mal
                    <ChevronDown className="h-3 w-3 ml-2 transition-transform duration-fast ease-standard group-data-[state=open]:rotate-180" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48 bg-card">
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

              {/* Dark mode toggle */}
              <TooltipProvider delayDuration={300}>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="ml-2 flex items-center gap-2">
                      <Sun className="h-4 w-4 text-muted-foreground" />
                      <Switch
                        checked={isDark}
                        onCheckedChange={setDark}
                        aria-label="Mørk modus"
                      />
                      <Moon className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">
                    <p>{isDark ? "Mørk modus" : "Lys modus"}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>

              {/* Notification Dropdown */}
              <NotificationDropdown className="ml-2" />

              {/* User + Logout */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="ml-2 flex items-center gap-2 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-card/40 transition-colors">
                    <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-semibold text-foreground uppercase">
                      {userEmail ? userEmail[0] : "?"}
                    </div>
                    {userEmail && (
                      <span className="hidden lg:inline text-xs font-medium">
                        {userEmail.split("@")[0]}
                      </span>
                    )}
                    <ChevronDown className="h-3 w-3" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-52 bg-card">
                  {userEmail && (
                    <div className="px-3 py-2 text-xs text-muted-foreground border-b border-border">
                      {userEmail}
                    </div>
                  )}
                  <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600 mt-1">
                    <LogOut className="h-4 w-4 mr-2" />
                    Logg ut
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
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
