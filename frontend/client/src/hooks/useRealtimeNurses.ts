import { useEffect, useCallback } from "react";
import { useWebSocket } from "./useWebSocket";
import { toast } from "sonner";
import { notificationService } from "@/lib/notifications";

export interface Nurse {
  id: string;
  name: string;
  name_ar?: string;
  skill_level: "JUNIOR" | "INTERMEDIATE" | "SENIOR" | "EXPERT";
  max_hours_per_week: number;
  preferences?: any;
}

export interface UseRealtimeNursesOptions {
  onNurseCreated?: (nurse: Nurse) => void;
  onNurseUpdated?: (nurse: Nurse) => void;
  onNurseDeleted?: (nurseId: string) => void;
  showToasts?: boolean;
}

export function useRealtimeNurses(options: UseRealtimeNursesOptions = {}) {
  const { on, off, isConnected } = useWebSocket();
  const { onNurseCreated, onNurseUpdated, onNurseDeleted, showToasts = true } = options;

  const handleNurseCreated = useCallback((nurse: Nurse) => {
    console.log("[Realtime] Nurse created:", nurse);
    if (showToasts) {
      toast.success(`New nurse added: ${nurse.name}`);
      notificationService.notifyNurseCreated(nurse.name);
    }
    onNurseCreated?.(nurse);
  }, [onNurseCreated, showToasts]);

  const handleNurseUpdated = useCallback((nurse: Nurse) => {
    console.log("[Realtime] Nurse updated:", nurse);
    if (showToasts) {
      toast.info(`Nurse updated: ${nurse.name}`);
      notificationService.notifyNurseUpdated(nurse.name);
    }
    onNurseUpdated?.(nurse);
  }, [onNurseUpdated, showToasts]);

  const handleNurseDeleted = useCallback((nurseId: string) => {
    console.log("[Realtime] Nurse deleted:", nurseId);
    if (showToasts) {
      toast.warning(`Nurse removed: ${nurseId}`);
      notificationService.notifyNurseDeleted(nurseId);
    }
    onNurseDeleted?.(nurseId);
  }, [onNurseDeleted, showToasts]);

  useEffect(() => {
    if (!isConnected) return;

    on("nurse:created", handleNurseCreated);
    on("nurse:updated", handleNurseUpdated);
    on("nurse:deleted", handleNurseDeleted);

    return () => {
      off("nurse:created", handleNurseCreated);
      off("nurse:updated", handleNurseUpdated);
      off("nurse:deleted", handleNurseDeleted);
    };
  }, [isConnected, on, off, handleNurseCreated, handleNurseUpdated, handleNurseDeleted]);

  return {
    isConnected,
  };
}
