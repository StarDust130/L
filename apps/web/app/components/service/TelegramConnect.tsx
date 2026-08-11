"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";

const TelegramConnect = () => {
  const { getToken } = useAuth();

  const [code, setCode] = useState<string | null>(null);
  const [expiresIn, setExpiresIn] = useState<number | null>(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!code || expiresIn === null) return;

    const timer = setInterval(() => {
      setExpiresIn((current) => {
        if (current === null || current <= 1) {
          clearInterval(timer);
          setCode(null);
          return null;
        }

        return current - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [code]);

  async function connectTelegram() {
    setLoading(true);

    try {
      const token = await getToken();

      if (!token) {
        throw new Error("Authentication required");
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/telegram/link-code`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        throw new Error("Failed to create Telegram code");
      }

      const data = await response.json();

      if (data.connected) {
        setConnected(true);
        return;
      }

      setCode(data.code);
      setExpiresIn(data.expires_in);
    } catch (error) {
      console.error("Telegram connection failed:", error);
    } finally {
      setLoading(false);
    }
  }

  const minutes = Math.floor((expiresIn ?? 0) / 60);
  const seconds = (expiresIn ?? 0) % 60;

  if (connected) {
    return (
      <div className="relative w-full max-w-md overflow-hidden rounded-3xl border border-emerald-500/20 bg-zinc-950 p-8 text-white shadow-2xl shadow-emerald-500/10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,0.16),transparent_45%)]" />

        <div className="relative">
          <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10 ring-1 ring-emerald-400/20">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500 text-2xl shadow-lg shadow-emerald-500/30">
              ✓
            </div>
          </div>

          <p className="mb-2 text-sm font-medium text-emerald-400">
            Connection successful
          </p>

          <h3 className="text-2xl font-semibold tracking-tight">
            Telegram connected
          </h3>

          <p className="mt-3 text-sm leading-6 text-zinc-400">
            You're all set. You can now chat with L directly from Telegram.
          </p>

          <div className="mt-6 flex items-center gap-3 rounded-2xl border border-white/5 bg-white/[0.03] p-4">
            <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-emerald-400" />
            <span className="text-sm text-zinc-300">Telegram is active</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="group relative w-full max-w-md overflow-hidden rounded-3xl border border-white/10 bg-zinc-950 p-8 text-white shadow-2xl shadow-black/40">
      {/* Animated background */}
      <div className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-sky-500/20 blur-3xl transition-all duration-700 group-hover:bg-sky-400/30" />
      <div className="pointer-events-none absolute -bottom-24 -left-24 h-64 w-64 rounded-full bg-violet-500/15 blur-3xl" />

      <div className="relative">
        {/* Header */}
        <div className="mb-8 flex items-start justify-between">
          <div>
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#229ED9]/10 ring-1 ring-[#229ED9]/20">
              <svg
                viewBox="0 0 24 24"
                className="h-7 w-7 fill-[#229ED9]"
                aria-hidden="true"
              >
                <path d="M21.5 3.5 18.2 20c-.25 1.17-.91 1.46-1.85.91l-5.08-3.74-2.45 2.36c-.27.27-.5.5-1.02.5l.36-5.17 9.41-8.5c.41-.36-.09-.56-.64-.2L5.3 13.51.26 11.93c-1.1-.35-1.12-1.1.23-1.63L20.2 2.68c.92-.34 1.72.21 1.3.82Z" />
              </svg>
            </div>

            <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-sky-400">
              Connect
            </p>

            <h3 className="text-2xl font-semibold tracking-tight">
              Connect Telegram
            </h3>

            <p className="mt-2 max-w-sm text-sm leading-6 text-zinc-400">
              Connect your Telegram account and chat with L anywhere.
            </p>
          </div>

          <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-medium text-zinc-400">
            SECURE
          </div>
        </div>

        {!code ? (
          <button
            onClick={connectTelegram}
            disabled={loading}
            className="group/button relative flex w-full items-center justify-center gap-3 overflow-hidden rounded-2xl bg-white px-5 py-4 text-sm font-semibold text-black transition-all duration-300 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-white/10 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-black/5 to-transparent transition-transform duration-700 group-hover/button:translate-x-full" />

            {loading ? (
              <>
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-black/20 border-t-black" />
                Generating secure code...
              </>
            ) : (
              <>
                Connect Telegram
                <span className="text-lg transition-transform duration-300 group-hover/button:translate-x-1">
                  →
                </span>
              </>
            )}
          </button>
        ) : (
          <div className="animate-in fade-in slide-in-from-bottom-3 duration-500">
            <div className="mb-5 rounded-2xl border border-sky-400/10 bg-sky-400/[0.04] p-5">
              <p className="mb-4 text-sm text-zinc-400">
                Open L on Telegram and send this code:
              </p>

              <div className="flex items-center justify-center rounded-xl border border-white/10 bg-black/30 py-5">
                <strong className="font-mono text-4xl font-bold tracking-[0.3em] text-white">
                  {code}
                </strong>
              </div>

              <div className="mt-4 flex items-center justify-between text-xs">
                <span className="text-zinc-500">Code expires in</span>

                <span
                  className={
                    expiresIn !== null && expiresIn < 30
                      ? "font-mono font-semibold text-red-400"
                      : "font-mono font-semibold text-sky-400"
                  }
                >
                  {minutes}:{seconds.toString().padStart(2, "0")}
                </span>
              </div>
            </div>

            <a
              href={process.env.NEXT_PUBLIC_TELEGRAM_BOT_URL}
              target="_blank"
              rel="noreferrer"
              className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#229ED9] px-5 py-4 text-sm font-semibold text-white shadow-lg shadow-[#229ED9]/20 transition-all duration-300 hover:-translate-y-0.5 hover:bg-[#1d91c9] hover:shadow-xl hover:shadow-[#229ED9]/30"
            >
              Open L on Telegram
              <span className="text-lg">↗</span>
            </a>

            <p className="mt-4 text-center text-xs text-zinc-600">
              Keep this page open while connecting.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TelegramConnect;
