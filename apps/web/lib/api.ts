import type { StreamChunk, StreamMetadata, FitResponse } from "./types";

// Frontend calls the same-origin `/api/...` path. In local dev this is
// rewritten to the FastAPI server (see apps/web/next.config.ts).
// In production behind a single domain the rewrite / proxy should handle it.
const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "/api";

export interface StreamCallbacks {
  onChunk: (text: string) => void;
  onMetadata: (data: StreamMetadata) => void;
  onDone: () => void;
  onError: (error: Error) => void;
}

export async function sendChatMessage(
  message: string,
  callbacks: StreamCallbacks
): Promise<void> {
  let settled = false;
  const finish = (which: "done" | "error", err?: Error) => {
    if (settled) return;
    settled = true;
    if (which === "done") callbacks.onDone();
    else callbacks.onError(err ?? new Error("Unknown error"));
  };

  let response: Response;
  try {
    response = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ message }),
    });
  } catch {
    finish("error", new Error("Could not connect to the assistant. Please try again."));
    return;
  }

  if (!response.ok) {
    finish("error", new Error(`Server error: ${response.status}. Please try again.`));
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    finish("error", new Error("No response body received."));
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";

      for (const raw of events) {
        const line = raw.trim();
        if (!line.startsWith("data:")) continue;
        const payload = line.slice(5).trim();
        if (!payload) continue;

        if (payload === "[DONE]") {
          finish("done");
          return;
        }

        try {
          const event = JSON.parse(payload) as StreamChunk | StreamMetadata;
          if (event.type === "chunk") {
            callbacks.onChunk((event as StreamChunk).content);
          } else if (event.type === "metadata") {
            callbacks.onMetadata(event as StreamMetadata);
          }
        } catch {
          // Malformed event — skip.
        }
      }
    }
  } catch {
    finish("error", new Error("Stream interrupted. Please try again."));
    return;
  } finally {
    try {
      reader.releaseLock();
    } catch {
      /* noop */
    }
  }

  finish("done");
}

export async function analyseFit(jobDescription: string): Promise<FitResponse> {
  const response = await fetch(`${API_BASE}/fit/analyse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_description: jobDescription }),
  });

  if (!response.ok) {
    throw new Error(`Fit analysis failed: ${response.status}`);
  }

  return response.json() as Promise<FitResponse>;
}
