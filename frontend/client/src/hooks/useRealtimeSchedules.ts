import { useEffect, useCallback } from "react";
import { useWebSocket } from "./useWebSocket";
import { toast } from "sonner";
import { notificationService } from "@/lib/notifications";

export interface Schedule {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  department: string;
  status: "active" | "completed" | "draft";
  created_at: string;
}

export interface UseRealtimeSchedulesOptions {
  onScheduleCreated?: (schedule: Schedule) => void;
  onScheduleUpdated?: (schedule: Schedule) => void;
  onScheduleDeleted?: (scheduleId: string) => void;
  showToasts?: boolean;
}

export function useRealtimeSchedules(options: UseRealtimeSchedulesOptions = {}) {
  const { on, off, isConnected } = useWebSocket();
  const { onScheduleCreated, onScheduleUpdated, onScheduleDeleted, showToasts = true } = options;

  const handleScheduleCreated = useCallback((schedule: Schedule) => {
    console.log("[Realtime] Schedule created:", schedule);
    if (showToasts) {
      toast.success(`New schedule created: ${schedule.name}`);
      notificationService.notifyScheduleCreated(schedule.name);
    }
    onScheduleCreated?.(schedule);
  }, [onScheduleCreated, showToasts]);

  const handleScheduleUpdated = useCallback((schedule: Schedule) => {
    console.log("[Realtime] Schedule updated:", schedule);
    if (showToasts) {
      toast.info(`Schedule updated: ${schedule.name}`);
      notificationService.notifyScheduleUpdated(schedule.name);
    }
    onScheduleUpdated?.(schedule);
  }, [onScheduleUpdated, showToasts]);

  const handleScheduleDeleted = useCallback((scheduleId: string) => {
    console.log("[Realtime] Schedule deleted:", scheduleId);
    if (showToasts) {
      toast.warning(`Schedule removed: ${scheduleId}`);
      notificationService.notifyScheduleDeleted(scheduleId);
    }
    onScheduleDeleted?.(scheduleId);
  }, [onScheduleDeleted, showToasts]);

  useEffect(() => {
    if (!isConnected) return;

    on("schedule:created", handleScheduleCreated);
    on("schedule:updated", handleScheduleUpdated);
    on("schedule:deleted", handleScheduleDeleted);

    return () => {
      off("schedule:created", handleScheduleCreated);
      off("schedule:updated", handleScheduleUpdated);
      off("schedule:deleted", handleScheduleDeleted);
    };
  }, [isConnected, on, off, handleScheduleCreated, handleScheduleUpdated, handleScheduleDeleted]);

  return {
    isConnected,
  };
}
