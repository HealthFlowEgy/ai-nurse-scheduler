import { useWebSocket } from "@/hooks/useWebSocket";
import { Wifi, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function ConnectionStatus() {
  const { isConnected } = useWebSocket();

  return (
    <Badge
      variant="outline"
      className={`flex items-center gap-2 ${
        isConnected
          ? "bg-green-50 text-green-700 border-green-200"
          : "bg-red-50 text-red-700 border-red-200"
      }`}
    >
      {isConnected ? (
        <>
          <Wifi className="h-3 w-3" />
          <span className="text-xs">Live</span>
        </>
      ) : (
        <>
          <WifiOff className="h-3 w-3" />
          <span className="text-xs">Offline</span>
        </>
      )}
    </Badge>
  );
}
