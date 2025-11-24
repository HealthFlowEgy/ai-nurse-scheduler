import { ReactNode, useState } from "react";
import { Link, useLocation } from "wouter";
import { 
  LayoutDashboard, 
  Users, 
  Calendar, 
  CalendarPlus,
  Menu,
  X,
  Languages,
  Shield,
  LogOut,
  UserCircle,
  Settings
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { APP_TITLE } from "@/const";
import { useAuth } from "@/contexts/AuthContext";
import { usePermission } from "@/hooks/usePermission";
import { ROLE_LABELS, ROLE_COLORS, type Role } from "../../../shared/permissions";

interface DashboardLayoutProps {
  children: ReactNode;
}

interface NavItem {
  href: string;
  label: string;
  labelAr: string;
  icon: React.ElementType;
  requireRole?: Role;
  requireAnyRole?: Role[];
}

const navItems: NavItem[] = [
  { href: "/", label: "Dashboard", labelAr: "لوحة التحكم", icon: LayoutDashboard },
  { href: "/nurses", label: "Nurses", labelAr: "الممرضات", icon: Users },
  { href: "/schedules", label: "Schedules", labelAr: "الجداول", icon: Calendar },
  { href: "/create-schedule", label: "Create Schedule", labelAr: "إنشاء جدول", icon: CalendarPlus, requireAnyRole: ["manager", "admin"] },
  { href: "/users", label: "User Management", labelAr: "إدارة المستخدمين", icon: Shield, requireRole: "admin" },
];

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [location] = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [language, setLanguage] = useState<"en" | "ar">("en");
  const { user, logout } = useAuth();

  const canAccessItem = (item: NavItem) => {
    if (!user) return false;
    if (item.requireRole && user.role !== item.requireRole) return false;
    if (item.requireAnyRole && !item.requireAnyRole.includes(user.role as Role)) return false;
    return true;
  };

  const filteredNavItems = navItems.filter(canAccessItem);

  const toggleLanguage = () => {
    setLanguage(prev => prev === "en" ? "ar" : "en");
  };

  const isActive = (href: string) => {
    if (href === "/") return location === "/";
    return location.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-background" dir={language === "ar" ? "rtl" : "ltr"} lang={language}>
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-card border-b border-border">
        <div className="flex items-center justify-between p-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <h1 className="text-lg font-semibold text-foreground">
            {language === "en" ? APP_TITLE : "جدولة الممرضات بالذكاء الاصطناعي"}
          </h1>
          <Button variant="ghost" size="icon" onClick={toggleLanguage}>
            <Languages className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 ${language === "ar" ? "right-0" : "left-0"} bottom-0 z-40
          w-64 bg-card ${language === "ar" ? "border-l" : "border-r"} border-border
          transform transition-transform duration-200 ease-in-out
          lg:translate-x-0
          ${sidebarOpen ? "translate-x-0" : (language === "ar" ? "translate-x-full" : "-translate-x-full")}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-border hidden lg:block">
            <h1 className="text-xl font-bold text-foreground">
              {language === "en" ? APP_TITLE : "جدولة الممرضات"}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              {language === "en" ? "HealthFlow RegTech" : "هيلث فلو ريج تك"}
            </p>
          </div>

          {/* User Info */}
          {user && (
            <div className="p-4 border-b border-border">
              <div className="flex items-center gap-3 mb-3">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-sm font-semibold text-primary">
                    {user.name?.charAt(0).toUpperCase() || "U"}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {user.name || "User"}
                  </p>
                  <Badge variant="outline" className={`text-xs ${ROLE_COLORS[user.role as Role]}`}>
                    {ROLE_LABELS[user.role as Role]}
                  </Badge>
                </div>
              </div>
              <div className="flex gap-2">
                <Link href="/profile">
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => setSidebarOpen(false)}>
                    <UserCircle className="h-4 w-4 mr-1" />
                    {language === "en" ? "Profile" : "الملف الشخصي"}
                  </Button>
                </Link>
                <Button variant="outline" size="sm" onClick={() => { logout(); setSidebarOpen(false); }}>
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 mt-16 lg:mt-0">
            {filteredNavItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link key={item.href} href={item.href}>
                  <a
                    className={`
                      flex items-center gap-3 px-4 py-3 rounded-lg
                      transition-colors duration-150
                      ${active 
                        ? "bg-primary text-primary-foreground" 
                        : "text-foreground hover:bg-accent hover:text-accent-foreground"
                      }
                    `}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    <span className="font-medium">
                      {language === "en" ? item.label : item.labelAr}
                    </span>
                  </a>
                </Link>
              );
            })}
          </nav>

          {/* Language Toggle - Desktop */}
          <div className="p-4 border-t border-border hidden lg:block">
            <Button
              variant="outline"
              className="w-full justify-start gap-3"
              onClick={toggleLanguage}
            >
              <Languages className="h-5 w-5" />
              <span>{language === "en" ? "العربية" : "English"}</span>
            </Button>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className={`${language === "ar" ? "lg:mr-64" : "lg:ml-64"} pt-16 lg:pt-0 min-h-screen relative z-10`}>
        <div className="p-4 md:p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
