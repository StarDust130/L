"use client";

import { auth } from "@clerk/nextjs/server";

import { useAuth } from "@clerk/nextjs";
import {
  AlertCircle,
  ArrowUpRight,
  BrainCircuit,
  CheckCircle2,
  FileText,
  FileUp,
  Gauge,
  Loader2,
  Settings2,
  Sparkles,
  UploadCloud,
} from "lucide-react";
import { useRef, useState } from "react";
import type { ChangeEvent, DragEvent } from "react";

type ExtractedResume = {
  filename: string;
  file_type: "pdf" | "docx" | "txt";
  text: string;
  character_count: number;
};

type UploadState = "idle" | "uploading" | "success" | "error";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const MAX_FILE_SIZE = 5 * 1024 * 1024;

export default   function DashboardPage() {
  // await auth.protect();
  const { getToken, isLoaded, isSignedIn } = useAuth();

  const inputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);
  const [uploadState, setUploadState] =
    useState<UploadState>("idle");
  const [selectedFileName, setSelectedFileName] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [resume, setResume] =
    useState<ExtractedResume | null>(null);

  async function uploadResume(file: File) {
    setErrorMessage("");
    setResume(null);

    const extension = file.name
      .split(".")
      .pop()
      ?.toLowerCase();

    if (!extension || !["pdf", "docx", "txt"].includes(extension)) {
      setUploadState("error");
      setErrorMessage(
        "Use a PDF, DOCX, or TXT resume.",
      );
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setUploadState("error");
      setErrorMessage(
        "Your resume must be smaller than 5 MB.",
      );
      return;
    }

    if (!isLoaded) {
      setUploadState("error");
      setErrorMessage("Authentication is still loading.");
      return;
    }

    if (!isSignedIn) {
      setUploadState("error");
      setErrorMessage("Please sign in before uploading.");
      return;
    }

    setSelectedFileName(file.name);
    setUploadState("uploading");

    try {
      const token = await getToken();

      if (!token) {
        throw new Error("Could not create a Clerk session token.");
      }

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${API_URL}/api/resumes/extract`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ?? "Resume upload failed.",
        );
      }

      setResume(data as ExtractedResume);
      setUploadState("success");
    } catch (error) {
      setUploadState("error");
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Something went wrong.",
      );
    }
  }

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (file) {
      void uploadResume(file);
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];

    if (file) {
      void uploadResume(file);
    }
  }

  return (
    <div className="min-h-screen bg-[#090b10] text-zinc-100">
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-white/[0.07] bg-[#0d1017] lg:flex">
        <div className="flex h-20 items-center gap-3 border-b border-white/[0.07] px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400 font-black text-slate-950">
            L
          </div>

          <div>
            <p className="font-semibold tracking-tight">
              L Intelligence
            </p>
            <p className="text-xs text-zinc-500">
              Career workspace
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          <div className="flex items-center gap-3 rounded-xl bg-white/[0.08] px-3 py-2.5 text-sm font-medium text-white">
            <Gauge className="h-4 w-4 text-cyan-300" />
            Overview
          </div>

          <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-zinc-500">
            <FileText className="h-4 w-4" />
            Resume profile
          </div>

          <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-zinc-500">
            <Settings2 className="h-4 w-4" />
            Settings
          </div>
        </nav>

        <div className="m-4 rounded-2xl border border-emerald-400/15 bg-emerald-400/[0.06] p-4">
          <div className="flex items-center gap-2 text-xs font-medium text-emerald-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            L is online
          </div>

          <p className="mt-2 text-xs leading-5 text-zinc-500">
            Your workspace is ready for its first signal.
          </p>
        </div>
      </aside>

      <main className="lg:pl-64">
        <div className="mx-auto max-w-7xl px-6 py-8 lg:px-10">
          <header className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-300">
                Workspace / Resume intelligence
              </p>

              <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">
                Give L your signal.
              </h1>

              <p className="mt-2 max-w-xl text-sm leading-6 text-zinc-400">
                Upload your resume and L will turn it into a clear,
                editable career profile.
              </p>
            </div>

            <div className="hidden items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.04] px-3 py-2 text-xs text-zinc-400 sm:flex">
              <BrainCircuit className="h-4 w-4 text-violet-300" />
              Profile setup
            </div>
          </header>

          <section className="mt-10 grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
            <div className="rounded-3xl border border-white/[0.08] bg-[#10141c] p-6 shadow-2xl shadow-black/20 sm:p-8">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 text-sm font-medium text-zinc-300">
                    <Sparkles className="h-4 w-4 text-cyan-300" />
                    Step 01
                  </div>

                  <h2 className="mt-3 text-xl font-semibold">
                    Upload your resume
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-zinc-500">
                    L currently accepts PDF, DOCX, and TXT files.
                  </p>
                </div>

                <div className="rounded-2xl bg-cyan-400/[0.08] p-3 text-cyan-300">
                  <FileUp className="h-5 w-5" />
                </div>
              </div>

              <div
                onDragOver={(event) => {
                  event.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={[
                  "mt-8 rounded-2xl border border-dashed p-8 text-center transition",
                  isDragging
                    ? "border-cyan-300 bg-cyan-300/[0.08]"
                    : "border-white/[0.13] bg-[#0b0e14] hover:border-white/25",
                ].join(" ")}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  className="hidden"
                />

                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white/[0.06] text-cyan-300">
                  {uploadState === "uploading" ? (
                    <Loader2 className="h-6 w-6 animate-spin" />
                  ) : (
                    <UploadCloud className="h-6 w-6" />
                  )}
                </div>

                <p className="mt-5 text-sm font-medium text-zinc-200">
                  {uploadState === "uploading"
                    ? "Reading your resume..."
                    : "Drop your resume here"}
                </p>

                <p className="mt-2 text-xs text-zinc-500">
                  or choose a file from your computer
                </p>

                <button
                  type="button"
                  onClick={() => inputRef.current?.click()}
                  disabled={uploadState === "uploading"}
                  className="mt-6 inline-flex items-center gap-2 rounded-xl bg-cyan-300 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Choose file
                  <ArrowUpRight className="h-4 w-4" />
                </button>

                <p className="mt-4 text-[11px] text-zinc-600">
                  Maximum size: 5 MB
                </p>
              </div>

              {selectedFileName && (
                <div className="mt-4 flex items-center gap-3 rounded-xl border border-white/[0.08] bg-white/[0.03] p-3">
                  <FileText className="h-4 w-4 text-zinc-400" />
                  <span className="truncate text-sm text-zinc-300">
                    {selectedFileName}
                  </span>
                </div>
              )}

              {errorMessage && (
                <div className="mt-4 flex items-start gap-3 rounded-xl border border-red-400/20 bg-red-400/[0.06] p-4 text-sm text-red-200">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-300" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {uploadState === "success" && (
                <div className="mt-4 flex items-start gap-3 rounded-xl border border-emerald-400/20 bg-emerald-400/[0.06] p-4 text-sm text-emerald-200">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" />
                  <span>
                    Resume text extracted successfully.
                  </span>
                </div>
              )}
            </div>

            <aside className="rounded-3xl border border-white/[0.08] bg-[#10141c] p-6">
              <div className="flex items-center gap-2 text-sm font-medium text-zinc-300">
                <BrainCircuit className="h-4 w-4 text-violet-300" />
                What L will do
              </div>

              <div className="mt-6 space-y-5">
                <div>
                  <p className="text-sm font-medium text-zinc-200">
                    Read
                  </p>
                  <p className="mt-1 text-xs leading-5 text-zinc-500">
                    Extract text from your document without changing it.
                  </p>
                </div>

                <div>
                  <p className="text-sm font-medium text-zinc-200">
                    Understand
                  </p>
                  <p className="mt-1 text-xs leading-5 text-zinc-500">
                    Later, Groq will organize your skills and goals.
                  </p>
                </div>

                <div>
                  <p className="text-sm font-medium text-zinc-200">
                    Confirm
                  </p>
                  <p className="mt-1 text-xs leading-5 text-zinc-500">
                    You stay in control and can edit every detail.
                  </p>
                </div>
              </div>

              <div className="mt-8 rounded-2xl border border-violet-300/15 bg-violet-300/[0.06] p-4">
                <p className="text-xs font-medium text-violet-200">
                  Privacy first
                </p>
                <p className="mt-2 text-xs leading-5 text-zinc-500">
                  Your resume is processed for your workspace only.
                </p>
              </div>
            </aside>
          </section>

          {resume && (
            <section className="mt-6 rounded-3xl border border-white/[0.08] bg-[#10141c] p-6 shadow-2xl shadow-black/20 sm:p-8">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">
                    Extracted text
                  </p>

                  <h2 className="mt-2 text-xl font-semibold">
                    {resume.filename}
                  </h2>
                </div>

                <span className="rounded-full border border-white/[0.08] px-3 py-1 text-xs text-zinc-500">
                  {resume.character_count.toLocaleString()} characters
                </span>
              </div>

              <pre className="mt-6 max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-2xl border border-white/[0.07] bg-[#0a0d12] p-5 text-sm leading-7 text-zinc-400">
                {resume.text}
              </pre>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}