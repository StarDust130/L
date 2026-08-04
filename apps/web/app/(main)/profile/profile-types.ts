export type RemotePreference =
  | "remote"
  | "hybrid"
  | "onsite"
  | "flexible"
  | "unknown";

export type CandidateProfile = {
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

export type ExtractedResume = {
  filename: string;
  file_type: "pdf" | "docx" | "txt";
  text: string;
  character_count: number;
};

export const emptyCandidateProfile: CandidateProfile = {
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

export const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function splitCommaList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function splitLines(value: string): string[] {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}
