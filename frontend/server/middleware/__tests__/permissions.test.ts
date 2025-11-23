import { describe, it, expect } from "vitest";
import { hasPermission, hasAnyPermission, hasAllPermissions, type Role, type Permission } from "../../../shared/permissions";

describe("Permission System", () => {
  describe("hasPermission", () => {
    it("should allow admin to access all permissions", () => {
      const adminRole: Role = "admin";
      expect(hasPermission(adminRole, "view:dashboard")).toBe(true);
      expect(hasPermission(adminRole, "create:nurse")).toBe(true);
      expect(hasPermission(adminRole, "delete:nurse")).toBe(true);
      expect(hasPermission(adminRole, "manage:users")).toBe(true);
    });

    it("should allow manager to create and edit but not delete nurses", () => {
      const managerRole: Role = "manager";
      expect(hasPermission(managerRole, "view:nurses")).toBe(true);
      expect(hasPermission(managerRole, "create:nurse")).toBe(true);
      expect(hasPermission(managerRole, "edit:nurse")).toBe(true);
      expect(hasPermission(managerRole, "delete:nurse")).toBe(false);
    });

    it("should restrict nurse role to view-only permissions", () => {
      const nurseRole: Role = "nurse";
      expect(hasPermission(nurseRole, "view:dashboard")).toBe(true);
      expect(hasPermission(nurseRole, "view:nurses")).toBe(true);
      expect(hasPermission(nurseRole, "create:nurse")).toBe(false);
      expect(hasPermission(nurseRole, "edit:nurse")).toBe(false);
      expect(hasPermission(nurseRole, "delete:nurse")).toBe(false);
    });

    it("should deny manager access to user management", () => {
      const managerRole: Role = "manager";
      expect(hasPermission(managerRole, "manage:users")).toBe(false);
    });

    it("should deny nurse access to schedule creation", () => {
      const nurseRole: Role = "nurse";
      expect(hasPermission(nurseRole, "create:schedule")).toBe(false);
    });
  });

  describe("hasAnyPermission", () => {
    it("should return true if user has at least one permission", () => {
      const managerRole: Role = "manager";
      const permissions: Permission[] = ["create:nurse", "delete:nurse"];
      expect(hasAnyPermission(managerRole, permissions)).toBe(true);
    });

    it("should return false if user has none of the permissions", () => {
      const nurseRole: Role = "nurse";
      const permissions: Permission[] = ["create:nurse", "delete:nurse"];
      expect(hasAnyPermission(nurseRole, permissions)).toBe(false);
    });
  });

  describe("hasAllPermissions", () => {
    it("should return true if user has all permissions", () => {
      const adminRole: Role = "admin";
      const permissions: Permission[] = ["create:nurse", "edit:nurse", "delete:nurse"];
      expect(hasAllPermissions(adminRole, permissions)).toBe(true);
    });

    it("should return false if user is missing any permission", () => {
      const managerRole: Role = "manager";
      const permissions: Permission[] = ["create:nurse", "delete:nurse"];
      expect(hasAllPermissions(managerRole, permissions)).toBe(false);
    });
  });

  describe("Role Hierarchy", () => {
    it("should have admin with most permissions", () => {
      const adminRole: Role = "admin";
      const managerRole: Role = "manager";
      const nurseRole: Role = "nurse";

      const allPermissions: Permission[] = [
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
      ];

      const adminPerms = allPermissions.filter(p => hasPermission(adminRole, p)).length;
      const managerPerms = allPermissions.filter(p => hasPermission(managerRole, p)).length;
      const nursePerms = allPermissions.filter(p => hasPermission(nurseRole, p)).length;

      expect(adminPerms).toBeGreaterThan(managerPerms);
      expect(managerPerms).toBeGreaterThan(nursePerms);
    });
  });

  describe("Export Permissions", () => {
    it("should allow manager and admin to export data", () => {
      expect(hasPermission("admin", "export:data")).toBe(true);
      expect(hasPermission("manager", "export:data")).toBe(true);
      expect(hasPermission("nurse", "export:data")).toBe(false);
    });
  });

  describe("Schedule Management", () => {
    it("should allow manager and admin to create schedules", () => {
      expect(hasPermission("admin", "create:schedule")).toBe(true);
      expect(hasPermission("manager", "create:schedule")).toBe(true);
      expect(hasPermission("nurse", "create:schedule")).toBe(false);
    });

    it("should only allow admin to delete schedules", () => {
      expect(hasPermission("admin", "delete:schedule")).toBe(true);
      expect(hasPermission("manager", "delete:schedule")).toBe(false);
      expect(hasPermission("nurse", "delete:schedule")).toBe(false);
    });
  });

  describe("User Management", () => {
    it("should only allow admin to manage users", () => {
      expect(hasPermission("admin", "manage:users")).toBe(true);
      expect(hasPermission("manager", "manage:users")).toBe(false);
      expect(hasPermission("nurse", "manage:users")).toBe(false);
    });
  });
});
