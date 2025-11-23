import { ReactNode } from "react";
import { useAuth } from "../contexts/AuthContext";
import { usePermission } from "../hooks/usePermission";
import type { Permission, Role } from "../../../shared/permissions";

interface PermissionGuardProps {
  children: ReactNode;
  permission?: Permission;
  role?: Role;
  anyRole?: Role[];
  fallback?: ReactNode;
}

/**
 * Component to conditionally render children based on permissions or roles
 * Use this for hiding/showing UI elements based on user permissions
 */
export function PermissionGuard({
  children,
  permission,
  role,
  anyRole,
  fallback = null,
}: PermissionGuardProps) {
  const { user, isAuthenticated } = useAuth();
  const { can } = usePermission();

  if (!isAuthenticated) {
    return <>{fallback}</>;
  }

  // Check role-based access
  if (role && user?.role !== role) {
    return <>{fallback}</>;
  }

  if (anyRole && !anyRole.includes(user?.role as Role)) {
    return <>{fallback}</>;
  }

  // Check permission-based access
  if (permission && !can(permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
