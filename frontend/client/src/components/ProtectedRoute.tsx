import { ReactNode } from "react";
import { Redirect } from "wouter";
import { useAuth } from "../contexts/AuthContext";
import { usePermission } from "../hooks/usePermission";
import type { Permission, Role } from "../../../shared/permissions";
import { AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";

interface ProtectedRouteProps {
  children: ReactNode;
  requirePermission?: Permission;
  requireRole?: Role;
  requireAnyRole?: Role[];
  fallback?: ReactNode;
}

export function ProtectedRoute({
  children,
  requirePermission,
  requireRole,
  requireAnyRole,
  fallback,
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const { can } = usePermission();

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Redirect to="/login" />;
  }

  // Check role-based access
  if (requireRole && user?.role !== requireRole) {
    return fallback || <AccessDenied requiredRole={requireRole} />;
  }

  if (requireAnyRole && !requireAnyRole.includes(user?.role as Role)) {
    return fallback || <AccessDenied requiredRoles={requireAnyRole} />;
  }

  // Check permission-based access
  if (requirePermission && !can(requirePermission)) {
    return fallback || <AccessDenied requiredPermission={requirePermission} />;
  }

  return <>{children}</>;
}

interface AccessDeniedProps {
  requiredRole?: Role;
  requiredRoles?: Role[];
  requiredPermission?: Permission;
}

function AccessDenied({ requiredRole, requiredRoles, requiredPermission }: AccessDeniedProps) {
  const { user } = useAuth();

  let message = "You don't have permission to access this page.";
  
  if (requiredRole) {
    message = `This page requires ${requiredRole} role.`;
  } else if (requiredRoles) {
    message = `This page requires one of the following roles: ${requiredRoles.join(", ")}.`;
  } else if (requiredPermission) {
    message = `This page requires the following permission: ${requiredPermission}.`;
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="max-w-md w-full">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-destructive/10 flex items-center justify-center">
              <AlertCircle className="h-6 w-6 text-destructive" />
            </div>
            <CardTitle>Access Denied</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">{message}</p>
          <p className="text-sm text-muted-foreground">
            Your current role: <span className="font-semibold text-foreground">{user?.role}</span>
          </p>
          <Button onClick={() => window.history.back()} className="w-full">
            Go Back
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
