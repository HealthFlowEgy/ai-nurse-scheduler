import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LogIn, Shield, Users, Calendar } from "lucide-react";
import { APP_TITLE } from "@/const";

export default function Login() {
  const handleLogin = () => {
    window.location.href = "/api/auth/login";
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-accent/5 p-4">
      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* Left side - Branding */}
        <div className="space-y-6">
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">
              {APP_TITLE}
            </h1>
            <p className="text-xl text-muted-foreground">
              AI-Powered Healthcare Workforce Management
            </p>
          </div>

          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Calendar className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Smart Scheduling</h3>
                <p className="text-sm text-muted-foreground">
                  AI-optimized nurse schedules with Ramadan support and labor law compliance
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Users className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Team Management</h3>
                <p className="text-sm text-muted-foreground">
                  Comprehensive nurse profiles with skill levels and preferences
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Shield className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Role-Based Access</h3>
                <p className="text-sm text-muted-foreground">
                  Secure access control for Nurses, Managers, and Administrators
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right side - Login Card */}
        <Card className="shadow-lg">
          <CardHeader className="text-center space-y-2">
            <CardTitle className="text-2xl">Welcome Back</CardTitle>
            <CardDescription>
              Sign in to access the nurse scheduling system
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={handleLogin} 
              className="w-full h-12 text-base"
              size="lg"
            >
              <LogIn className="h-5 w-5 mr-2" />
              Sign In with Manus
            </Button>

            <div className="text-center space-y-2 pt-4 border-t border-border">
              <p className="text-sm text-muted-foreground">
                Secure authentication powered by Manus OAuth
              </p>
              <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground">
                <span>🔒 Encrypted</span>
                <span>•</span>
                <span>🌍 Multi-language</span>
                <span>•</span>
                <span>⚡ Fast</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
