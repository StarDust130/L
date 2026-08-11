"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@clerk/nextjs";

type Props = {
  token: string;
};

export default function TelegramPage({ token }: Props) {
  const { getToken } = useAuth();

  const hasConnected = useRef(false);

  const [status, setStatus] = useState<"connecting" | "success" | "error">(
    "connecting",
  );

  useEffect(() => {
    if (hasConnected.current) {
      return;
    }

    hasConnected.current = true;

    async function connectTelegram() {
      try {
        const clerkToken = await getToken();

        if (!clerkToken) {
          throw new Error("Clerk token missing");
        }

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/telegram/connect?token=${encodeURIComponent(token)}`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${clerkToken}`,
            },
          },
        );

        if (!response.ok) {
          const data = await response.json().catch(() => null);

          throw new Error(data?.detail ?? "Telegram connection failed");
        }

        setStatus("success");
      } catch (error) {
        console.error("Telegram connection failed:", error);
        setStatus("error");
      }
    }

    connectTelegram();
  }, [getToken, token]);

  if (status === "connecting") {
    return <p>Connecting L to Telegram...</p>;
  }

  if (status === "error") {
    return (
      <main>
        <h1>Could not connect Telegram</h1>
        <p>We couldn't connect your Telegram account.</p>
      </main>
    );
  }

  return (
    <main>
      <h1>Telegram connected ✓</h1>

      <p>Your L account is now connected to Telegram.</p>

      <a href="https://t.me/L_jobless_bot">Open Telegram →</a>
    </main>
  );
}
