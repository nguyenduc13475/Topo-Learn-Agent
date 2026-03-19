import { useEffect, useRef } from "react";
import { useAuth } from "@/hooks/use-auth";

export interface DocumentStatusEvent {
  event: "DOCUMENT_STATUS_UPDATED";
  payload: {
    document_id: number;
    status: "processing" | "completed" | "failed";
    error?: string;
  };
}

export interface GraphStatusEvent {
  event: "GRAPH_STATUS_UPDATED";
  payload: {
    document_id: number;
    status: "pending" | "building" | "completed" | "failed";
    error?: string;
  };
}

export type WebSocketMessage = DocumentStatusEvent | GraphStatusEvent;

export function useAppWebSocket(
  onMessage?: (message: WebSocketMessage) => void,
) {
  const { token } = useAuth();
  const savedCallback = useRef(onMessage);

  // Exponential Backoff tracked via ref to prevent useEffect loops
  const reconnectAttempts = useRef(0);
  const maxAttempts = 5;

  useEffect(() => {
    savedCallback.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    if (!token) return;

    let socket: WebSocket;
    let pingInterval: NodeJS.Timeout;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      const isSecure = window.location.protocol === "https:";
      const wsProtocol = isSecure ? "wss:" : "ws:";
      let wsUrl = "";

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

      if (apiUrl.startsWith("http")) {
        wsUrl = apiUrl.replace(/^http/, "ws") + `/ws/ws?token=${token}`;
      } else {
        wsUrl = `${wsProtocol}//${window.location.host}${apiUrl}/ws/ws?token=${token}`;
      }

      console.log(
        `[WebSocket] Connecting... Attempt ${reconnectAttempts.current}`,
      );
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        console.log("[WebSocket] Connected successfully");
        reconnectAttempts.current = 0; // Reset attempts on success
        pingInterval = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send("ping");
          }
        }, 30000);
      };

      socket.onmessage = (event) => {
        if (event.data === "pong") return;
        try {
          const data = JSON.parse(event.data) as WebSocketMessage;
          if (savedCallback.current) {
            savedCallback.current(data);
          }
        } catch (e) {
          console.error("Error parsing WS message", e);
        }
      };

      socket.onclose = (event) => {
        console.log("[WebSocket] Disconnected", event.reason);
        clearInterval(pingInterval);

        // 1008 indicates Authentication Failed (Expired/Invalid Token).
        // Halt reconnections to prevent server spam.
        if (event.code === 1008) {
          console.error(
            "[WebSocket] Authentication failed. Stopping reconnection attempts.",
          );
          return;
        }

        if (reconnectAttempts.current < maxAttempts) {
          const timeout = Math.pow(2, reconnectAttempts.current) * 1000;
          console.log(`[WebSocket] Reconnecting in ${timeout}ms...`);
          reconnectTimeout = setTimeout(() => {
            reconnectAttempts.current += 1;
            connect();
          }, timeout);
        } else {
          console.error(
            "[WebSocket] Max reconnect attempts reached. Please refresh.",
          );
        }
      };

      socket.onerror = (err) => {
        console.error("[WebSocket] Error occurred", err);
        // Do not force close here; let the browser naturally hit onclose
      };
    };

    connect();

    return () => {
      clearInterval(pingInterval);
      clearTimeout(reconnectTimeout);
      if (socket) {
        socket.onclose = null;
        socket.close();
      }
    };
  }, [token]); // no reconnectAttempts to prevent infinite loops
}
