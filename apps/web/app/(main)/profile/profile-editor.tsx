"use client";

import { ArrowLeft, Check, FilePenLine, LoaderCircle, Save } from "lucide-react";

import {
  type CandidateProfile,
  type RemotePreference,
  splitCommaList,
  splitLines,
} from "./profile-types";

type ProfileEditorProps = {
  profile: CandidateProfile;
  isSaving: boolean;
  isSaved: boolean;
  notice: string;
  onBack: () => void;
  onSave: () => void;
  onChange: <Key extends keyof CandidateProfile>(
    field: Key,
    value: CandidateProfile[Key],
  ) => void;
};

export function ProfileEditor({
  profile,
  isSaving,
  isSaved,
  notice,
  onBack,
  onSave,
  onChange,
}: ProfileEditorProps) {
  return (
    <section className="overflow-hidden border border-[#171310]/20 bg-[#f7f3eb]">
      <header className="flex flex-col gap-6 border-b border-[#171310]/15 p-5 sm:p-7 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <button
            type="button"
            onClick={onBack}
            className="rule-label inline-flex items-center gap-2 text-[#806d60] transition hover:text-[#8d2030]"
          >
            <ArrowLeft size={15} />
            Profile sources
          </button>
          <p className="rule-label mt-8 text-[#806d60]">Candidate profile / review</p>
          <h1 className="mt-3 font-display text-5xl tracking-[-0.065em] sm:text-6xl">
            Make the file yours.
          </h1>
        </div>
        <div className="flex items-center gap-3 border border-[#171310]/15 bg-[#eee8db] px-4 py-3 text-sm text-[#5f564e]">
          {isSaved ? <Check size={17} className="text-[#8d2030]" /> : <FilePenLine size={17} />}
          {isSaved ? "Profile saved" : "Review before saving"}
        </div>
      </header>

      <div className="w-full">
       

        <div className="p-5 sm:p-7 lg:p-9">
          <div className="grid gap-x-8 gap-y-7 md:grid-cols-2">
            <TextField
              label="Full name"
              value={profile.full_name ?? ""}
              onChange={(value) => onChange("full_name", value || null)}
            />
            <TextField
              label="Years of experience"
              type="number"
              min="0"
              step="0.5"
              value={profile.years_of_experience?.toString() ?? ""}
              onChange={(value) =>
                onChange("years_of_experience", value === "" ? null : Number(value))
              }
            />
            <TextField
              label="Target roles"
              hint="Separate with commas"
              value={profile.target_roles.join(", ")}
              onChange={(value) => onChange("target_roles", splitCommaList(value))}
            />
            <TextField
              label="Locations"
              hint="Separate with commas"
              value={profile.locations.join(", ")}
              onChange={(value) => onChange("locations", splitCommaList(value))}
            />
            <TextField
              label="Core skills"
              hint="Separate with commas"
              value={profile.skills.join(", ")}
              onChange={(value) => onChange("skills", splitCommaList(value))}
            />
            <TextField
              label="Work authorization"
              value={profile.work_authorization ?? ""}
              onChange={(value) => onChange("work_authorization", value || null)}
            />
            <SelectField
              label="Work preference"
              value={profile.remote_preference}
              onChange={(value) => onChange("remote_preference", value)}
            />
            <TextField
              label="Relevant links"
              hint="Separate with commas"
              value={profile.links.join(", ")}
              onChange={(value) => onChange("links", splitCommaList(value))}
            />
          </div>

          <div className="mt-8 grid gap-8 md:grid-cols-2">
            <TextAreaField
              label="Experience"
              hint="One item per line"
              value={profile.experience.join("\n")}
              onChange={(value) => onChange("experience", splitLines(value))}
            />
            <TextAreaField
              label="Education"
              hint="One item per line"
              value={profile.education.join("\n")}
              onChange={(value) => onChange("education", splitLines(value))}
            />
          </div>

          <div className="mt-9 flex flex-col gap-4 border-t border-[#171310]/15 pt-6 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-[#665d55]" role="status">
              {notice}
            </p>
            <button
              type="button"
              onClick={onSave}
              disabled={isSaving}
              className="inline-flex items-center justify-center gap-3 bg-[#8d2030] px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-[#651522] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSaving ? <LoaderCircle size={17} className="animate-spin" /> : <Save size={17} />}
              Save profile
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function TextField({
  label,
  hint,
  type = "text",
  min,
  step,
  value,
  onChange,
}: {
  label: string;
  hint?: string;
  type?: string;
  min?: string;
  step?: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="border-b border-[#171310]/20 pb-3">
      <span className="rule-label block text-[#806d60]">{label}</span>
      {hint ? <span className="mt-1 block text-xs text-[#8b8178]">{hint}</span> : null}
      <input
        type={type}
        min={min}
        step={step}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-3 w-full bg-transparent text-base outline-none placeholder:text-[#aaa095]"
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
    <label className="border-b border-[#171310]/20 pb-3">
      <span className="rule-label block text-[#806d60]">{label}</span>
      <span className="mt-1 block text-xs text-[#8b8178]">{hint}</span>
      <textarea
        rows={6}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-3 w-full resize-y bg-transparent text-base leading-6 outline-none"
      />
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: RemotePreference;
  onChange: (value: RemotePreference) => void;
}) {
  return (
    <label className="border-b border-[#171310]/20 pb-3">
      <span className="rule-label block text-[#806d60]">{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as RemotePreference)}
        className="mt-3 w-full bg-transparent text-base outline-none"
      >
        <option value="unknown">Not specified</option>
        <option value="remote">Remote</option>
        <option value="hybrid">Hybrid</option>
        <option value="onsite">On-site</option>
        <option value="flexible">Flexible</option>
      </select>
    </label>
  );
}
