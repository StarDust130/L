"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";

type Props = {
  token: string;
};

export default function TelegramPage({ token }: Props) {
  const { getToken } = useAuth();

  const [status, setStatus] = useState<"connecting" | "success" | "error">(
    "connecting",
  );

  useEffect(() => {
    async function connect() {
      try {
        // 🔐 Get the authenticated Clerk session token.
        const clerkToken = await getToken();

        if (!clerkToken) {
          throw new Error("Authentication token missing");
        }

        // 🔗 Connect Telegram to this authenticated user.
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/telegram/?token=${encodeURIComponent(token)}`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${clerkToken}`,
            },
          },
        );

        if (!response.ok) {
          throw new Error("Telegram connection failed");
        }

        setStatus("success");
      } catch {
        setStatus("error");
      }
    }

    connect();
  }, [getToken, token]);

  if (status === "connecting") {
    return (
      <main>
        <p>Connecting L to Telegram...</p>
      </main>
    );
  }

  if (status === "error") {
    return (
      <main>
        <h1>Could not connect Telegram</h1>
        <p>This link may have expired or already been used.</p>
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
