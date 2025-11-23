/**
 * Role-Based Access Control (RBAC) Configuration
 * 
 * Defines roles, permissions, and access control rules for the nurse scheduler
 */

export type Role = "nurse" | "manager" | "admin";

export type Permission =
  | "view:dashboard"
  | "view:nurses"
  | "create:nurse"
  | "edit:nurse"
  | "delete:nurse"
  | "view:schedules"
  | "create:schedule"
  | "edit:schedule"
  | "delete:schedule"
  | "export:data"
  | "manage:users"
  | "view:analytics";

/**
 * Permission matrix defining what each role can do
 */
export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  nurse: [
    "view:dashboard",
    "view:nurses",
    "view:schedules",
  ],
  manager: [
    "view:dashboard",
    "view:nurses",
    "create:nurse",
    "edit:nurse",
    "view:schedules",
    "create:schedule",
    "edit:schedule",
    "export:data",
    "view:analytics",
  ],
  admin: [
    "view:dashboard",
    "view:nurses",
    "create:nurse",
    "edit:nurse",
    "delete:nurse",
    "view:schedules",
    "create:schedule",
    "edit:schedule",
    "delete:schedule",
    "export:data",
    "manage:users",
    "view:analytics",
  ],
};

/**
 * Check if a role has a specific permission
 */
export function hasPermission(role: Role, permission: Permission): boolean {
  return ROLE_PERMISSIONS[role].includes(permission);
}

/**
 * Check if a role has any of the specified permissions
 */
export function hasAnyPermission(role: Role, permissions: Permission[]): boolean {
  return permissions.some(permission => hasPermission(role, permission));
}

/**
 * Check if a role has all of the specified permissions
 */
export function hasAllPermissions(role: Role, permissions: Permission[]): boolean {
  return permissions.every(permission => hasPermission(role, permission));
}

/**
 * Get all permissions for a role
 */
export function getRolePermissions(role: Role): Permission[] {
  return ROLE_PERMISSIONS[role];
}

/**
 * Role display names
 */
export const ROLE_LABELS: Record<Role, string> = {
  nurse: "Nurse",
  manager: "Manager",
  admin: "Administrator",
};

/**
 * Role descriptions
 */
export const ROLE_DESCRIPTIONS: Record<Role, string> = {
  nurse: "Can view schedules and nurse information",
  manager: "Can manage nurses and create schedules",
  admin: "Full system access including user management",
};

/**
 * Role badge colors for UI
 */
export const ROLE_COLORS: Record<Role, string> = {
  nurse: "bg-blue-100 text-blue-700 border-blue-200",
  manager: "bg-purple-100 text-purple-700 border-purple-200",
  admin: "bg-red-100 text-red-700 border-red-200",
};
