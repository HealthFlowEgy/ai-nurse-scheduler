import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";
import { requireRole, requireAnyRole } from "../middleware/permissions";
import { getDb } from "../db";
import { users } from "../../drizzle/schema";
import { eq } from "drizzle-orm";

export const usersRouter = router({
  /**
   * Get all users (Admin and Manager only)
   */
  list: publicProcedure
    .use(async ({ ctx, next }) => requireAnyRole(["admin", "manager"])(ctx) && next())
    .query(async () => {
      const db = await getDb();
      if (!db) {
        throw new Error("Database not available");
      }

      const allUsers = await db.select().from(users);
      return allUsers;
    }),

  /**
   * Get current user info
   */
  me: publicProcedure.query(async ({ ctx }) => {
    return ctx.user;
  }),

  /**
   * Update user role (Admin only)
   */
  updateRole: publicProcedure
    .use(async ({ ctx, next }) => requireRole("admin")(ctx) && next())
    .input(
      z.object({
        userId: z.number(),
        role: z.enum(["nurse", "manager", "admin"]),
      })
    )
    .mutation(async ({ input }) => {
      const db = await getDb();
      if (!db) {
        throw new Error("Database not available");
      }

      await db
        .update(users)
        .set({ role: input.role })
        .where(eq(users.id, input.userId));

      return { success: true };
    }),
});
