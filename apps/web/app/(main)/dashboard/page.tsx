"use client";

import {
  ArrowLeft,
  ArrowUpRight,
  Check,
  FileText,
  LoaderCircle,
  PenLine,
  Save,
  Sparkles,
  Upload,
} from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import { ChangeEvent, useEffect, useState } from "react";

type RemotePreference = "remote" | "hybrid" | "onsite" | "flexible" | "unknown";

type CandidateProfile = {
  full_name: string | null;
  target_roles: string[];
  skills: string[];
  experience: string[];
  education: string[];
  locations: string[];
  remote_preference: RemotePreference;
  years_of_experience: number | null;
  work_authorization: string | null;
  links: string[];
};

const emptyProfile: CandidateProfile = {
  full_name: "",
  target_roles: [],
  skills: [],
  experience: [],
  education: [],
  locations: [],
  remote_preference: "unknown",
  years_of_experience: null,
  work_authorization: "",
  links: [],
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function splitValues(value: string): string[] {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function joinValues(value: string[]): string {
  return value.join(", ");
}

export default function DashboardPage() {
  const { getToken } = useAuth();

  const [profile, setProfile] = useState<CandidateProfile>(emptyProfile);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [screen, setScreen] = useState<"source" | "review">("source");

  const [source, setSource] = useState<"resume" | "manual">("resume");

  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function loadSavedProfile() {
      const token = await getToken();

      if (!token) return;

      const response = await fetch(`${apiUrl}/api/profile`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) return;

      const savedProfile = await response.json();

      if (savedProfile) {
        setProfile(savedProfile);
        setScreen("review");
        setSaved(true);
      }
    }

    loadSavedProfile();
  }, [getToken]);

  function updateProfile(field: keyof CandidateProfile, value: unknown) {
    setProfile((current) => ({
      ...current,
      [field]: value,
    }));

    setSaved(false);
  }

  async function createProfileFromResume() {
    if (!selectedFile) {
      setMessage("Choose a resume first.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const token = await getToken();

      if (!token) {
        throw new Error("You are not signed in.");
      }

      const formData = new FormData();
      formData.append("file", selectedFile);

      // 📄 Send the resume to FastAPI
      const resumeResponse = await fetch(`${apiUrl}/api/resumes/extract`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!resumeResponse.ok) {
        throw new Error("Resume parsing failed.");
      }

      const extractedResume = await resumeResponse.json();

      // 🤖 Ask FastAPI to send text to Groq
      const profileResponse = await fetch(`${apiUrl}/api/profile/extract`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_text: extractedResume.text,
        }),
      });

      if (!profileResponse.ok) {
        throw new Error("AI profile extraction failed.");
      }

      const generatedProfile = await profileResponse.json();

      setProfile(generatedProfile);
      setScreen("review");
      setMessage("Profile created. Please review every field.");
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Something went wrong.",
      );
    } finally {
      setLoading(false);
    }
  }

  function startManualProfile() {
    setSource("manual");
    setProfile(emptyProfile);
    setScreen("review");
    setSaved(false);
    setMessage("");
  }

  async function saveProfile() {
    setLoading(true);
    setMessage("");

    try {
      const token = await getToken();

      if (!token) {
        throw new Error("You are not signed in.");
      }

      // ✅ Send only the reviewed profile to FastAPI
      const response = await fetch(`${apiUrl}/api/profile`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(profile),
      });

      if (!response.ok) {
        throw new Error("Profile could not be saved.");
      }

      const savedProfile = await response.json();

      setProfile(savedProfile);
      setSaved(true);
      setMessage("Your profile is saved.");
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Something went wrong.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#e8e5dc] px-4 py-6 text-[#111817] sm:px-8">
      <div className="mx-auto max-w-7xl overflow-hidden rounded-[2rem] border border-[#14211f]/15 bg-[#f8f6f0] shadow-[0_20px_80px_rgba(30,55,50,0.16)]">
        <header className="flex items-center justify-between border-b border-[#14211f]/15 px-6 py-5 sm:px-10">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[#49605a]">
              L / Profile Studio
            </p>
            <h1 className="mt-2 font-serif text-3xl tracking-[-0.04em] sm:text-4xl">
              Build your candidate profile
            </h1>
          </div>

          <div className="hidden items-center gap-2 rounded-full border border-[#14211f]/15 px-4 py-2 text-xs font-medium sm:flex">
            <span className="h-2 w-2 rounded-full bg-[#c9a227]" />
            Phase 02
          </div>
        </header>

        {screen === "source" ? (
          <section className="grid min-h-[650px] lg:grid-cols-[0.75fr_1.25fr]">
            <div className="flex flex-col justify-between bg-[#203f39] p-8 text-[#f5f1e7] sm:p-12">
              <div>
                <Sparkles size={22} strokeWidth={1.5} />

                <p className="mt-20 max-w-sm font-serif text-4xl leading-[1.05] tracking-[-0.04em] sm:text-6xl">
                  Give L the raw material.
                </p>

                <p className="mt-6 max-w-sm text-sm leading-6 text-[#d2ddd5]">
                  Upload your resume or create your profile by hand. L will
                  prepare the information for your daily job search.
                </p>
              </div>

              <div className="border-t border-[#d2ddd5]/30 pt-5 text-xs uppercase tracking-[0.2em] text-[#d2ddd5]">
                Private by design
              </div>
            </div>

            <div className="p-8 sm:p-12">
              <div className="flex gap-3">
                <button
                  onClick={() => setSource("resume")}
                  className={`rounded-full px-5 py-3 text-sm transition ${
                    source === "resume"
                      ? "bg-[#111817] text-white"
                      : "border border-[#111817]/20"
                  }`}
                >
                  Resume upload
                </button>

                <button
                  onClick={() => setSource("manual")}
                  className={`rounded-full px-5 py-3 text-sm transition ${
                    source === "manual"
                      ? "bg-[#111817] text-white"
                      : "border border-[#111817]/20"
                  }`}
                >
                  Manual form
                </button>
              </div>

              {source === "resume" ? (
                <div className="mt-20">
                  <div className="border-b border-[#111817]/20 pb-6">
                    <p className="text-xs uppercase tracking-[0.25em] text-[#60716a]">
                      Import resume
                    </p>
                    <h2 className="mt-4 font-serif text-4xl tracking-[-0.04em]">
                      Start with your story.
                    </h2>
                  </div>

                  <label className="mt-10 flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-[#203f39]/40 bg-[#eeece5] p-8 text-center transition hover:bg-[#e5e2d9]">
                    <Upload size={28} strokeWidth={1.5} />
                    <span className="mt-5 text-sm font-medium">
                      {selectedFile
                        ? selectedFile.name
                        : "Choose PDF, DOCX, or TXT"}
                    </span>
                    <span className="mt-2 text-xs text-[#60716a]">
                      Maximum file size: 5 MB
                    </span>

                    <input
                      type="file"
                      accept=".pdf,.docx,.txt"
                      className="hidden"
                      onChange={(event: ChangeEvent<HTMLInputElement>) =>
                        setSelectedFile(event.target.files?.[0] ?? null)
                      }
                    />
                  </label>

                  <button
                    onClick={createProfileFromResume}
                    disabled={loading || !selectedFile}
                    className="mt-6 flex w-full items-center justify-center gap-3 rounded-full bg-[#111817] px-6 py-4 text-sm font-semibold text-white transition hover:bg-[#294d45] disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {loading ? (
                      <LoaderCircle className="animate-spin" size={18} />
                    ) : (
                      <Sparkles size={18} />
                    )}
                    Create profile with L
                    <ArrowUpRight size={18} />
                  </button>
                </div>
              ) : (
                <div className="mt-20">
                  <p className="text-xs uppercase tracking-[0.25em] text-[#60716a]">
                    Manual profile
                  </p>

                  <h2 className="mt-4 max-w-lg font-serif text-4xl tracking-[-0.04em]">
                    Tell us what kind of work feels right.
                  </h2>

                  <p className="mt-5 max-w-md text-sm leading-6 text-[#60716a]">
                    This creates the same profile structure as the resume path.
                    You can edit everything before saving.
                  </p>

                  <button
                    onClick={startManualProfile}
                    className="mt-10 flex items-center gap-3 rounded-full bg-[#111817] px-6 py-4 text-sm font-semibold text-white"
                  >
                    Begin manually
                    <ArrowUpRight size={18} />
                  </button>
                </div>
              )}

              {message && (
                <p className="mt-5 text-sm text-[#7a4c25]">{message}</p>
              )}
            </div>
          </section>
        ) : (
          <ProfileReview
            profile={profile}
            loading={loading}
            saved={saved}
            message={message}
            onBack={() => setScreen("source")}
            onSave={saveProfile}
            onUpdate={updateProfile}
          />
        )}
      </div>
    </main>
  );
}

type ProfileReviewProps = {
  profile: CandidateProfile;
  loading: boolean;
  saved: boolean;
  message: string;
  onBack: () => void;
  onSave: () => void;
  onUpdate: (field: keyof CandidateProfile, value: unknown) => void;
};

function ProfileReview({
  profile,
  loading,
  saved,
  message,
  onBack,
  onSave,
  onUpdate,
}: ProfileReviewProps) {
  return (
    <section className="grid lg:grid-cols-[0.7fr_1.3fr]">
      <aside className="bg-[#203f39] p-8 text-[#f5f1e7] sm:p-12">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-[#d2ddd5]"
        >
          <ArrowLeft size={16} />
          Back
        </button>

        <p className="mt-24 text-xs uppercase tracking-[0.25em] text-[#b9ccc0]">
          Review room
        </p>

        <h2 className="mt-5 font-serif text-5xl leading-[0.95] tracking-[-0.05em]">
          Make it sound like you.
        </h2>

        <p className="mt-7 max-w-sm text-sm leading-6 text-[#d2ddd5]">
          AI can organize your resume, but you are the final decision-maker.
          Correct anything before saving.
        </p>

        <div className="mt-20 border-t border-[#d2ddd5]/30 pt-5 text-sm text-[#d2ddd5]">
          {saved ? (
            <span className="flex items-center gap-2">
              <Check size={16} />
              Profile saved
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <PenLine size={16} />
              Draft profile
            </span>
          )}
        </div>
      </aside>

      <div className="p-8 sm:p-12">
        <div className="flex items-start justify-between border-b border-[#111817]/15 pb-6">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-[#60716a]">
              Candidate profile
            </p>
            <h2 className="mt-3 font-serif text-4xl tracking-[-0.04em]">
              Your working identity
            </h2>
          </div>

          <FileText
            className="hidden text-[#60716a] sm:block"
            size={28}
            strokeWidth={1.5}
          />
        </div>

        <div className="mt-10 grid gap-8 sm:grid-cols-2">
          <TextField
            label="Full name"
            value={profile.full_name ?? ""}
            onChange={(value) => onUpdate("full_name", value)}
          />

          <TextField
            label="Years of experience"
            type="number"
            value={
              profile.years_of_experience === null
                ? ""
                : String(profile.years_of_experience)
            }
            onChange={(value) =>
              onUpdate("years_of_experience", value ? Number(value) : null)
            }
          />

          <TextField
            label="Target roles"
            value={joinValues(profile.target_roles)}
            onChange={(value) => onUpdate("target_roles", splitValues(value))}
          />

          <TextField
            label="Locations"
            value={joinValues(profile.locations)}
            onChange={(value) => onUpdate("locations", splitValues(value))}
          />

          <TextField
            label="Skills"
            value={joinValues(profile.skills)}
            onChange={(value) => onUpdate("skills", splitValues(value))}
          />

          <TextField
            label="Work authorization"
            value={profile.work_authorization ?? ""}
            onChange={(value) => onUpdate("work_authorization", value)}
          />

          <label className="border-b border-[#111817]/25 pb-3">
            <span className="block text-xs uppercase tracking-[0.18em] text-[#60716a]">
              Work preference
            </span>

            <select
              value={profile.remote_preference}
              onChange={(event) =>
                onUpdate(
                  "remote_preference",
                  event.target.value as RemotePreference,
                )
              }
              className="mt-3 w-full bg-transparent text-base outline-none"
            >
              <option value="unknown">Not specified</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-site</option>
              <option value="flexible">Flexible</option>
            </select>
          </label>

          <TextField
            label="Links"
            value={joinValues(profile.links)}
            onChange={(value) => onUpdate("links", splitValues(value))}
          />
        </div>

        <div className="mt-10 grid gap-8 sm:grid-cols-2">
          <TextAreaField
            label="Experience"
            hint="One item per line"
            value={profile.experience.join("\n")}
            onChange={(value) => onUpdate("experience", splitValues(value))}
          />

          <TextAreaField
            label="Education"
            hint="One item per line"
            value={profile.education.join("\n")}
            onChange={(value) => onUpdate("education", splitValues(value))}
          />
        </div>

        {message && (
          <p className="mt-7 flex items-center gap-2 text-sm text-[#49605a]">
            {saved && <Check size={16} />}
            {message}
          </p>
        )}

        <button
          onClick={onSave}
          disabled={loading}
          className="mt-8 flex items-center gap-3 rounded-full bg-[#111817] px-7 py-4 text-sm font-semibold text-white transition hover:bg-[#294d45] disabled:opacity-50"
        >
          {loading ? (
            <LoaderCircle className="animate-spin" size={18} />
          ) : (
            <Save size={18} />
          )}
          Save profile
        </button>
      </div>
    </section>
  );
}

function TextField({
  label,
  value,
  type = "text",
  onChange,
}: {
  label: string;
  value: string;
  type?: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="border-b border-[#111817]/25 pb-3">
      <span className="block text-xs uppercase tracking-[0.18em] text-[#60716a]">
        {label}
      </span>

      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-3 w-full bg-transparent text-base outline-none placeholder:text-[#9aa49e]"
      />
    </label>
  );
}

function TextAreaField({
  label,
  hint,
  value,
  onChange,
}: {
  label: string;
  hint: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="border-b border-[#111817]/25 pb-3">
      <span className="block text-xs uppercase tracking-[0.18em] text-[#60716a]">
        {label}
      </span>

      <span className="mt-2 block text-xs text-[#9aa49e]">{hint}</span>

      <textarea
        rows={5}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-3 w-full resize-none bg-transparent text-base outline-none"
      />
    </label>
  );
}
