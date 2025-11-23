import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Bell, BellOff } from "lucide-react";
import { notificationService } from "@/lib/notifications";
import { toast } from "sonner";

export default function NotificationSettings() {
  const [permission, setPermission] = useState<NotificationPermission>("default");
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    setIsSupported(notificationService.isSupported());
    if (notificationService.isSupported()) {
      setPermission(Notification.permission as NotificationPermission);
    }
  }, []);

  const handleEnableNotifications = async () => {
    const result = await notificationService.requestPermission();
    setPermission(result);
    
    if (result === "granted") {
      toast.success("Notifications enabled successfully");
      // Send test notification
      await notificationService.send({
        title: "Notifications Enabled",
        body: "You will now receive updates about schedule changes",
      });
    } else if (result === "denied") {
      toast.error("Notification permission denied. Please enable it in your browser settings.");
    }
  };

  if (!isSupported) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BellOff className="h-5 w-5" />
            Notifications Not Supported
          </CardTitle>
          <CardDescription>
            Your browser does not support push notifications
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Push Notifications
        </CardTitle>
        <CardDescription>
          Get notified about schedule updates and nurse changes
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">
              Status: {permission === "granted" ? "Enabled" : permission === "denied" ? "Blocked" : "Not Enabled"}
            </p>
            <p className="text-sm text-muted-foreground">
              {permission === "granted" 
                ? "You will receive notifications for important updates"
                : permission === "denied"
                ? "Notifications are blocked. Please enable them in browser settings."
                : "Enable notifications to stay updated on schedule changes"}
            </p>
          </div>
          {permission !== "granted" && permission !== "denied" && (
            <Button onClick={handleEnableNotifications}>
              <Bell className="h-4 w-4 mr-2" />
              Enable Notifications
            </Button>
          )}
        </div>

        {permission === "granted" && (
          <div className="pt-4 border-t">
            <p className="text-sm text-muted-foreground mb-2">
              You will be notified when:
            </p>
            <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
              <li>A new schedule is created</li>
              <li>An existing schedule is updated</li>
              <li>A nurse is added or updated</li>
              <li>Important system changes occur</li>
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
