import { useEffect, useState, useCallback, useRef } from "react";
import { io, Socket } from "socket.io-client";

export interface WebSocketStatus {
  connected: boolean;
  timestamp: number | null;
}

export interface UseWebSocketReturn {
  socket: Socket | null;
  status: WebSocketStatus;
  isConnected: boolean;
  emit: (event: string, data: any) => void;
  on: (event: string, callback: (...args: any[]) => void) => void;
  off: (event: string, callback?: (...args: any[]) => void) => void;
}

export function useWebSocket(): UseWebSocketReturn {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [status, setStatus] = useState<WebSocketStatus>({
    connected: false,
    timestamp: null,
  });
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // Create socket connection
    const newSocket = io({
      path: "/api/socket.io",
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    socketRef.current = newSocket;
    setSocket(newSocket);

    // Connection event handlers
    newSocket.on("connect", () => {
      console.log("[WebSocket] Connected");
      setStatus({
        connected: true,
        timestamp: Date.now(),
      });
    });

    newSocket.on("disconnect", (reason) => {
      console.log("[WebSocket] Disconnected:", reason);
      setStatus({
        connected: false,
        timestamp: Date.now(),
      });
    });

    newSocket.on("connection:status", (data: WebSocketStatus) => {
      console.log("[WebSocket] Status update:", data);
      setStatus(data);
    });

    newSocket.on("connect_error", (error) => {
      console.error("[WebSocket] Connection error:", error);
    });

    // Cleanup on unmount
    return () => {
      console.log("[WebSocket] Cleaning up connection");
      newSocket.close();
      socketRef.current = null;
    };
  }, []);

  const emit = useCallback((event: string, data: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data);
    } else {
      console.warn("[WebSocket] Cannot emit, socket not connected");
    }
  }, []);

  const on = useCallback((event: string, callback: (...args: any[]) => void) => {
    socketRef.current?.on(event, callback);
  }, []);

  const off = useCallback((event: string, callback?: (...args: any[]) => void) => {
    if (callback) {
      socketRef.current?.off(event, callback);
    } else {
      socketRef.current?.off(event);
    }
  }, []);

  return {
    socket,
    status,
    isConnected: status.connected,
    emit,
    on,
    off,
  };
}
