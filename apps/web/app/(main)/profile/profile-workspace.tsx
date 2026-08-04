"use client";

import { useAuth } from "@clerk/nextjs";
import {
  ArrowUpRight,
  FileText,
  LoaderCircle,
  PenLine,
  ScanSearch,
  Upload,
} from "lucide-react";
import { useEffect, useState } from "react";

import { ProfileEditor } from "./profile-editor";
import {
  apiUrl,
  type CandidateProfile,
  type ExtractedResume,
  emptyCandidateProfile,
} from "./profile-types";

type ProfileScreen = "source" | "review";
type RequestState = "idle" | "extracting" | "saving";

const acceptedExtensions = ["pdf", "docx", "txt"];
const maxResumeSize = 5 * 1024 * 1024;

export function ProfileWorkspace() {
  const { getToken } = useAuth();
  const [profile, setProfile] = useState<CandidateProfile>(emptyCandidateProfile);
  const [screen, setScreen] = useState<ProfileScreen>("source");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [isSaved, setIsSaved] = useState(false);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    async function loadProfile() {
      const token = await getToken();

      if (!token) return;

      const response = await fetch(`${apiUrl}/api/profile`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) return;

      const savedProfile = (await response.json()) as CandidateProfile | null;

      if (savedProfile) {
        setProfile(savedProfile);
        setScreen("review");
        setIsSaved(true);
        setNotice("Your saved profile is ready to review.");
      }
    }

    loadProfile();
  }, [getToken]);

  function updateProfile<Key extends keyof CandidateProfile>(
    field: Key,
    value: CandidateProfile[Key],
  ) {
    setProfile((current) => ({ ...current, [field]: value }));
    setIsSaved(false);
    setNotice("Unsaved changes.");
  }

  function beginManualProfile() {
    setProfile(emptyCandidateProfile);
    setScreen("review");
    setIsSaved(false);
    setNotice("Fill in only what you want L to use.");
  }

  function selectResume(file: File | null) {
    if (!file) return;

    const extension = file.name.split(".").pop()?.toLowerCase();

    if (!extension || !acceptedExtensions.includes(extension)) {
      setNotice("Choose a PDF, DOCX, or TXT resume.");
      return;
    }

    if (file.size > maxResumeSize) {
      setNotice("Your resume must be 5 MB or smaller.");
      return;
    }

    setSelectedFile(file);
    setNotice(`${file.name} is ready to analyze.`);
  }

  async function createProfileFromResume() {
    if (!selectedFile) {
      setNotice("Choose a resume before starting the analysis.");
      return;
    }

    setRequestState("extracting");
    setNotice("L is reading your resume.");

    try {
      const token = await getToken();

      if (!token) throw new Error("Your session has ended. Sign in again.");

      const formData = new FormData();
      formData.append("file", selectedFile);

      const resumeResponse = await fetch(`${apiUrl}/api/resumes/extract`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!resumeResponse.ok) {
        throw new Error(await readApiError(resumeResponse, "Resume parsing failed."));
      }

      const extractedResume = (await resumeResponse.json()) as ExtractedResume;

      setNotice("L is shaping your profile.");

      const profileResponse = await fetch(`${apiUrl}/api/profile/extract`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ resume_text: extractedResume.text }),
      });

      if (!profileResponse.ok) {
        throw new Error(
          await readApiError(profileResponse, "AI profile extraction failed."),
        );
      }

      setProfile((await profileResponse.json()) as CandidateProfile);
      setScreen("review");
      setIsSaved(false);
      setNotice("Profile drafted from your resume. Review every detail.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Something went wrong.");
    } finally {
      setRequestState("idle");
    }
  }

  async function saveProfile() {
    setRequestState("saving");
    setNotice("Saving your profile.");

    try {
      const token = await getToken();

      if (!token) throw new Error("Your session has ended. Sign in again.");

      const response = await fetch(`${apiUrl}/api/profile`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(profile),
      });

      if (!response.ok) {
        throw new Error(await readApiError(response, "Profile could not be saved."));
      }

      setProfile((await response.json()) as CandidateProfile);
      setIsSaved(true);
      setNotice("Profile saved. L will use this as its search lens.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Something went wrong.");
    } finally {
      setRequestState("idle");
    }
  }

  if (screen === "review") {
    return (
      <ProfileEditor
        profile={profile}
        isSaving={requestState === "saving"}
        isSaved={isSaved}
        notice={notice}
        onBack={() => setScreen("source")}
        onSave={saveProfile}
        onChange={updateProfile}
      />
    );
  }

  const isExtracting = requestState === "extracting";

  return (
    <section className="overflow-hidden border border-[#171310]/20 bg-[#f7f3eb]">
      <header className="flex flex-col gap-5 border-b border-[#171310]/15 p-5 sm:flex-row sm:items-end sm:justify-between sm:p-7">
        <div>
          <p className="rule-label text-[#806d60]">Candidate profile / intake</p>
          <h1 className="mt-3 font-display text-5xl tracking-[-0.065em] sm:text-6xl">
            Start your file.
          </h1>
        </div>
        <p className="max-w-sm text-sm leading-6 text-[#665d55] sm:text-right">
          Add information once. You can edit everything before L ever uses it.
        </p>
      </header>

      <div className="grid gap-px bg-[#171310]/15 lg:grid-cols-2">
        <article className="paper-grain case-corners relative bg-[#1b1714] p-6 text-[#f7f2e8] sm:p-8">
          <div className="flex items-start justify-between border-b border-white/20 pb-6">
            <div>
              <p className="rule-label text-[#d8c9b2]">Method 01</p>
              <h2 className="mt-3 font-display text-4xl tracking-[-0.055em]">Read my resume.</h2>
            </div>
            <ScanSearch size={28} className="text-[#d8c9b2]" strokeWidth={1.4} />
          </div>

          <p className="mt-7 max-w-md text-sm leading-7 text-[#d7cfc2]">
            Upload the version you want L to understand. It extracts text first, then creates a profile draft for you to approve.
          </p>

          <label className="mt-8 flex min-h-44 cursor-pointer flex-col items-center justify-center border border-dashed border-white/35 bg-white/5 p-6 text-center transition hover:bg-white/10">
            <Upload size={23} strokeWidth={1.5} />
            <span className="mt-4 text-sm font-medium">
              {selectedFile ? selectedFile.name : "Choose a resume"}
            </span>
            <span className="mt-2 text-xs text-white/55">PDF, DOCX, or TXT / 5 MB maximum</span>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              className="sr-only"
              onChange={(event) => selectResume(event.target.files?.[0] ?? null)}
            />
          </label>

          <button
            type="button"
            onClick={createProfileFromResume}
            disabled={!selectedFile || isExtracting}
            className="mt-5 inline-flex w-full items-center justify-center gap-3 border border-[#f7f2e8] bg-[#f7f2e8] px-5 py-3.5 text-sm font-semibold text-[#171310] transition hover:bg-transparent hover:text-[#f7f2e8] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isExtracting ? <LoaderCircle size={17} className="animate-spin" /> : <ScanSearch size={17} />}
            {isExtracting ? "Building profile" : "Analyze resume"}
            <ArrowUpRight size={16} />
          </button>
        </article>

        <article className="relative bg-[#f7f3eb] p-6 sm:p-8">
          <div className="flex items-start justify-between border-b border-[#171310]/15 pb-6">
            <div>
              <p className="rule-label text-[#806d60]">Method 02</p>
              <h2 className="mt-3 font-display text-4xl tracking-[-0.055em]">Write it yourself.</h2>
            </div>
            <PenLine size={27} className="text-[#8d2030]" strokeWidth={1.4} />
          </div>

          <p className="mt-7 max-w-md text-sm leading-7 text-[#665d55]">
            No resume? No problem. Give L your target roles, skills, preferences, and experience directly.
          </p>

          <div className="mt-8 grid min-h-44 place-items-center border border-[#171310]/15 bg-[#eee8db] p-6 text-center">
            <FileText size={28} className="text-[#8d2030]" strokeWidth={1.4} />
            <p className="mt-4 max-w-xs text-sm leading-6 text-[#665d55]">
              You remain the source of truth. Nothing is guessed, and every field stays editable.
            </p>
          </div>

          <button
            type="button"
            onClick={beginManualProfile}
            className="mt-5 inline-flex w-full items-center justify-center gap-3 bg-[#8d2030] px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-[#651522]"
          >
            Fill in profile manually
            <ArrowUpRight size={16} />
          </button>
        </article>
      </div>

      <footer className="flex min-h-14 items-center border-t border-[#171310]/15 px-5 text-sm text-[#665d55] sm:px-7" role="status">
        {notice || "Your profile is private and connected only to your account."}
      </footer>
    </section>
  );
}

async function readApiError(response: Response, fallback: string): Promise<string> {
  const body = (await response.json().catch(() => null)) as { detail?: unknown } | null;

  return typeof body?.detail === "string" ? body.detail : fallback;
}
