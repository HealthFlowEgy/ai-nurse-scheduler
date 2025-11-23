import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Users as UsersIcon, Shield, Edit } from "lucide-react";
import { toast } from "sonner";
import ConnectionStatus from "@/components/ConnectionStatus";
import { ROLE_LABELS, ROLE_COLORS, ROLE_DESCRIPTIONS, type Role } from "../../../shared/permissions";
import type { User } from "../../../drizzle/schema";

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState<string | null>(null);
  const [selectedRole, setSelectedRole] = useState<Role>("nurse");

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch("/api/users");
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error("Failed to fetch users:", error);
      toast.error("Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId: number, newRole: Role) => {
    try {
      const response = await fetch(`/api/users/${userId}/role`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: newRole }),
      });

      if (response.ok) {
        setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
        toast.success("User role updated successfully");
        setEditingUser(null);
      } else {
        toast.error("Failed to update user role");
      }
    } catch (error) {
      console.error("Failed to update role:", error);
      toast.error("Failed to update user role");
    }
  };

  const getRoleBadgeColor = (role: string) => {
    return ROLE_COLORS[role as Role] || "bg-gray-100 text-gray-700 border-gray-200";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading users...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-foreground">User Management</h1>
            <ConnectionStatus />
          </div>
          <p className="text-muted-foreground">
            Manage user roles and permissions
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{users.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Administrators
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {users.filter(u => u.role === "admin").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Managers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {users.filter(u => u.role === "manager").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Nurses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {users.filter(u => u.role === "nurse").length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Role Descriptions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {(Object.keys(ROLE_DESCRIPTIONS) as Role[]).map(role => (
          <Card key={role} className="border-l-4" style={{ borderLeftColor: role === "admin" ? "#ef4444" : role === "manager" ? "#a855f7" : "#3b82f6" }}>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                <CardTitle className="text-lg">{ROLE_LABELS[role]}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{ROLE_DESCRIPTIONS[role]}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Users List */}
      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {users.map(user => (
              <div
                key={user.id}
                className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/5 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1">
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <UsersIcon className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-foreground">{user.name || "Unknown User"}</p>
                      <Badge variant="outline" className={getRoleBadgeColor(user.role)}>
                        {ROLE_LABELS[user.role as Role]}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{user.email || "No email"}</p>
                    <p className="text-xs text-muted-foreground">
                      Last signed in: {new Date(user.lastSignedIn).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {editingUser === user.openId ? (
                    <>
                      <Select value={selectedRole} onValueChange={(value) => setSelectedRole(value as Role)}>
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="nurse">Nurse</SelectItem>
                          <SelectItem value="manager">Manager</SelectItem>
                          <SelectItem value="admin">Admin</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button size="sm" onClick={() => handleRoleChange(user.id, selectedRole)}>
                        Save
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => setEditingUser(null)}>
                        Cancel
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setEditingUser(user.openId);
                        setSelectedRole(user.role as Role);
                      }}
                    >
                      <Edit className="h-4 w-4 mr-1" />
                      Change Role
                    </Button>
                  )}
                </div>
              </div>
            ))}

            {users.length === 0 && (
              <div className="text-center py-12">
                <UsersIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-lg font-medium text-foreground">No users found</p>
                <p className="text-sm text-muted-foreground mt-1">Users will appear here after they sign in</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
