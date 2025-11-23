import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Calendar, Clock, TrendingUp } from "lucide-react";
import ConnectionStatus from "@/components/ConnectionStatus";
import NotificationSettings from "@/components/NotificationSettings";

export default function Dashboard() {
  const stats = [
    {
      title: "Total Nurses",
      titleAr: "إجمالي الممرضات",
      value: "48",
      icon: Users,
      description: "Active staff members",
      descriptionAr: "أعضاء الطاقم النشطين",
      color: "text-blue-600"
    },
    {
      title: "Active Schedules",
      titleAr: "الجداول النشطة",
      value: "3",
      icon: Calendar,
      description: "Current month",
      descriptionAr: "الشهر الحالي",
      color: "text-green-600"
    },
    {
      title: "Total Hours",
      titleAr: "إجمالي الساعات",
      value: "2,304",
      icon: Clock,
      description: "This month",
      descriptionAr: "هذا الشهر",
      color: "text-purple-600"
    },
    {
      title: "Satisfaction",
      titleAr: "الرضا",
      value: "87%",
      icon: TrendingUp,
      description: "Nurse preference match",
      descriptionAr: "تطابق تفضيلات الممرضات",
      color: "text-orange-600"
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <ConnectionStatus />
        </div>
        <p className="text-muted-foreground">
          Welcome to the AI-Enhanced Nurse Scheduler
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-5 w-5 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-foreground">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stat.description}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Notification Settings */}
      <NotificationSettings />

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Schedules</CardTitle>
            <CardDescription>Latest generated schedules</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: "December 2025", date: "Created 2 days ago", status: "Active" },
                { name: "November 2025", date: "Created 1 week ago", status: "Completed" },
                { name: "October 2025", date: "Created 1 month ago", status: "Completed" }
              ].map((schedule, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg border border-border">
                  <div>
                    <p className="font-medium text-foreground">{schedule.name}</p>
                    <p className="text-sm text-muted-foreground">{schedule.date}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    schedule.status === "Active" 
                      ? "bg-green-100 text-green-700" 
                      : "bg-gray-100 text-gray-700"
                  }`}>
                    {schedule.status}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>AI-Enhanced Scheduler Information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Optimization Engine</span>
                <span className="text-sm font-medium text-green-600">Operational</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Demand Forecasting</span>
                <span className="text-sm font-medium text-green-600">Active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Fatigue Prediction</span>
                <span className="text-sm font-medium text-green-600">Active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Labor Law Compliance</span>
                <span className="text-sm font-medium text-green-600">Enabled</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Ramadan Scheduling</span>
                <span className="text-sm font-medium text-blue-600">Ready</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
