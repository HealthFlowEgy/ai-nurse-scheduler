import { useAuth } from "../contexts/AuthContext";
import { hasPermission, hasAnyPermission, hasAllPermissions, type Permission, type Role } from "../../../shared/permissions";

/**
 * Hook to check user permissions
 */
export function usePermission() {
  const { user } = useAuth();

  const can = (permission: Permission): boolean => {
    if (!user) return false;
    return hasPermission(user.role as Role, permission);
  };

  const canAny = (permissions: Permission[]): boolean => {
    if (!user) return false;
    return hasAnyPermission(user.role as Role, permissions);
  };

  const canAll = (permissions: Permission[]): boolean => {
    if (!user) return false;
    return hasAllPermissions(user.role as Role, permissions);
  };

  return {
    can,
    canAny,
    canAll,
  };
}
