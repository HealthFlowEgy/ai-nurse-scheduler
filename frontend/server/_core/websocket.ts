import { Server as HTTPServer } from "http";
import { Server as SocketIOServer, Socket } from "socket.io";

export interface WebSocketEvents {
  // Nurse events
  "nurse:created": (nurse: any) => void;
  "nurse:updated": (nurse: any) => void;
  "nurse:deleted": (nurseId: string) => void;
  
  // Schedule events
  "schedule:created": (schedule: any) => void;
  "schedule:updated": (schedule: any) => void;
  "schedule:deleted": (scheduleId: string) => void;
  
  // Connection events
  "connection:status": (status: { connected: boolean; timestamp: number }) => void;
}

let io: SocketIOServer | null = null;

export function initializeWebSocket(httpServer: HTTPServer): SocketIOServer {
  if (io) {
    return io;
  }

  io = new SocketIOServer(httpServer, {
    cors: {
      origin: "*", // In production, specify your frontend URL
      methods: ["GET", "POST"],
      credentials: true
    },
    path: "/api/socket.io",
    transports: ["websocket", "polling"]
  });

  io.on("connection", (socket: Socket) => {
    console.log(`[WebSocket] Client connected: ${socket.id}`);

    // Send connection confirmation
    socket.emit("connection:status", {
      connected: true,
      timestamp: Date.now()
    });

    // Handle disconnection
    socket.on("disconnect", (reason) => {
      console.log(`[WebSocket] Client disconnected: ${socket.id}, reason: ${reason}`);
    });

    // Handle errors
    socket.on("error", (error) => {
      console.error(`[WebSocket] Socket error for ${socket.id}:`, error);
    });
  });

  console.log("[WebSocket] Server initialized");
  return io;
}

export function getWebSocketServer(): SocketIOServer | null {
  return io;
}

// Helper functions to broadcast events
export function broadcastNurseCreated(nurse: any) {
  io?.emit("nurse:created", nurse);
}

export function broadcastNurseUpdated(nurse: any) {
  io?.emit("nurse:updated", nurse);
}

export function broadcastNurseDeleted(nurseId: string) {
  io?.emit("nurse:deleted", nurseId);
}

export function broadcastScheduleCreated(schedule: any) {
  io?.emit("schedule:created", schedule);
}

export function broadcastScheduleUpdated(schedule: any) {
  io?.emit("schedule:updated", schedule);
}

export function broadcastScheduleDeleted(scheduleId: string) {
  io?.emit("schedule:deleted", scheduleId);
}
