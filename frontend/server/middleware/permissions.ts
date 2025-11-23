import { TRPCError } from "@trpc/server";
import type { TrpcContext } from "../_core/context";
import { hasPermission, type Permission, type Role } from "../../shared/permissions";

/**
 * Check if the current user has a specific permission
 */
export function requirePermission(permission: Permission) {
  return (ctx: TrpcContext) => {
    if (!ctx.user) {
      throw new TRPCError({
        code: "UNAUTHORIZED",
        message: "You must be logged in to perform this action",
      });
    }

    const userRole = ctx.user.role as Role;
    if (!hasPermission(userRole, permission)) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: `You don't have permission to perform this action. Required: ${permission}`,
      });
    }

    return ctx;
  };
}

/**
 * Check if the current user has a specific role
 */
export function requireRole(role: Role) {
  return (ctx: TrpcContext) => {
    if (!ctx.user) {
      throw new TRPCError({
        code: "UNAUTHORIZED",
        message: "You must be logged in to perform this action",
      });
    }

    if (ctx.user.role !== role) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: `You must be a ${role} to perform this action`,
      });
    }

    return ctx;
  };
}

/**
 * Check if the current user has any of the specified roles
 */
export function requireAnyRole(roles: Role[]) {
  return (ctx: TrpcContext) => {
    if (!ctx.user) {
      throw new TRPCError({
        code: "UNAUTHORIZED",
        message: "You must be logged in to perform this action",
      });
    }

    const userRole = ctx.user.role as Role;
    if (!roles.includes(userRole)) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: `You must be one of [${roles.join(", ")}] to perform this action`,
      });
    }

    return ctx;
  };
}

/**
 * Require authentication (any logged-in user)
 */
export function requireAuth(ctx: TrpcContext) {
  if (!ctx.user) {
    throw new TRPCError({
      code: "UNAUTHORIZED",
      message: "You must be logged in to perform this action",
    });
  }
  return ctx;
}
