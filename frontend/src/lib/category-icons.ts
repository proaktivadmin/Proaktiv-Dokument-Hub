import type { LucideIcon } from "lucide-react";
import {
  AlertCircle,
  BookOpen,
  Briefcase,
  Building,
  Building2,
  CheckCircle,
  ClipboardList,
  CreditCard,
  File,
  FileCheck,
  FileCheck2,
  FilePlus,
  FileQuestion,
  FileSpreadsheet,
  FileText,
  Folder,
  FolderTree,
  Gavel,
  Home,
  Info,
  InfoIcon,
  Landmark,
  Mail,
  Megaphone,
  MessageCircle,
  MessageSquare,
  Receipt,
  Scale,
  Send,
  Shield,
  ShieldCheck,
  Type,
  Users,
} from "lucide-react";

const iconMap: Record<string, LucideIcon> = {
  // Folders
  Folder,
  FolderTree,
  // Files
  File,
  FileText,
  FileSpreadsheet,
  FileCheck,
  FileCheck2,
  FilePlus,
  FileQuestion,
  // Buildings & Places
  Home,
  Building,
  Building2,
  Landmark,
  // People
  Users,
  // Communication
  Mail,
  Send,
  MessageSquare,
  MessageCircle,
  Megaphone,
  // Legal & Business
  Shield,
  ShieldCheck,
  Scale,
  Gavel,
  Briefcase,
  // Finance
  Receipt,
  CreditCard,
  // Info & Status
  Info,
  InfoIcon,
  AlertCircle,
  CheckCircle,
  // Text
  Type,
  BookOpen,
  ClipboardList,
};

export function getCategoryIcon(iconName?: string | null): LucideIcon {
  if (!iconName) return Folder;
  return iconMap[iconName] ?? Folder;
}
