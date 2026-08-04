"use client";

import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
};

export default function Home() {
  const [apiStatus, setApiStatus] = useState("Checking...");
  const [error, setError] = useState("");

  useEffect(() => {
    async function checkApi() {
      try {
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

        const response = await fetch(`${apiUrl}/health`);

        if (!response.ok) {
          throw new Error("API request failed");
        }

        const data: HealthResponse = await response.json();
        setApiStatus(data.status);
      } catch {
        setError("L API is not reachable");
      }
    }

    checkApi();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 px-6 text-white">
      <div className="w-full max-w-2xl rounded-3xl border border-zinc-800 bg-zinc-900 p-8 shadow-2xl">
        <p className="mb-3 text-sm font-medium uppercase tracking-[0.3em] text-violet-400">
          Project L
        </p>

        <h1 className="text-4xl font-bold tracking-tight">
          Your AI job-finding agent 🕵️‍♂️
        </h1>

        <p className="mt-4 text-zinc-400">
          L will find better internships and junior software jobs for you.
        </p>

        <div className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
          <p className="text-sm text-zinc-400">Backend status</p>

          {error ? (
            <p className="mt-2 font-semibold text-red-400">{error}</p>
          ) : (
            <p className="mt-2 font-semibold text-emerald-400">{apiStatus}</p>
          )}
        </div>
      </div>
    </main>
  );
}
