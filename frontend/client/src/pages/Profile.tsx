import { useAuth } from "@/contexts/AuthContext";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { UserCircle, Mail, Calendar, Shield, LogOut } from "lucide-react";
import { ROLE_LABELS, ROLE_COLORS, ROLE_PERMISSIONS, type Role, type Permission } from "../../../shared/permissions";

export default function Profile() {
  const { user, logout } = useAuth();

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-muted-foreground">Please log in to view your profile.</p>
      </div>
    );
  }

  const userPermissions = ROLE_PERMISSIONS[user.role as Role] || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Profile</h1>
        <p className="text-muted-foreground mt-2">View and manage your account information</p>
      </div>

      {/* User Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserCircle className="h-5 w-5" />
            User Information
          </CardTitle>
          <CardDescription>Your account details and role</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center gap-4">
            <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-2xl font-bold text-primary">
                {user.name?.charAt(0).toUpperCase() || "U"}
              </span>
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-semibold text-foreground">{user.name || "User"}</h2>
              <Badge variant="outline" className={`mt-2 ${ROLE_COLORS[user.role as Role]}`}>
                {ROLE_LABELS[user.role as Role]}
              </Badge>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="flex items-center gap-3 p-4 border border-border rounded-lg">
              <Mail className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium text-foreground">{user.email || "Not provided"}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 border border-border rounded-lg">
              <Shield className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Role</p>
                <p className="font-medium text-foreground">{ROLE_LABELS[user.role as Role]}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 border border-border rounded-lg">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Last Sign In</p>
                <p className="font-medium text-foreground">
                  {new Date(user.lastSignedIn).toLocaleDateString()}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 border border-border rounded-lg">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Member Since</p>
                <p className="font-medium text-foreground">
                  {new Date(user.createdAt).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Permissions Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Permissions
          </CardTitle>
          <CardDescription>What you can do in the system</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 md:grid-cols-2">
            {userPermissions.map((permission: Permission) => (
              <div
                key={permission}
                className="flex items-center gap-2 p-3 border border-border rounded-lg"
              >
                <div className="h-2 w-2 rounded-full bg-green-500" />
                <span className="text-sm font-medium text-foreground capitalize">
                  {permission.replace(/_/g, " ")}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Account Actions</CardTitle>
          <CardDescription>Manage your account</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="destructive" onClick={logout}>
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
