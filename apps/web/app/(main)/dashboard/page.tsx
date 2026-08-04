import Link from "next/link";
import {
  ArrowUpRight,
  Clock3,
  FilePenLine,
  Radar,
  Send,
} from "lucide-react";

const statusCards = [
  {
    label: "Profile signal",
    value: "Ready for review",
    detail: "Keep your preferences accurate.",
    code: "01",
  },
  {
    label: "Daily brief",
    value: "Not scheduled",
    detail: "Telegram delivery arrives in a later phase.",
    code: "02",
  },
  {
    label: "Job sources",
    value: "Field not active",
    detail: "Discovery starts when the agent is built.",
    code: "03",
  },
];

export default function DashboardPage() {
  return (
    <section className="space-y-5 sm:space-y-7">
      <header className="flex flex-col gap-5 border-b border-[#171310]/15 pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="rule-label text-[#806d60]">Operations / overview</p>
          <h1 className="mt-3 font-display text-5xl tracking-[-0.065em] sm:text-6xl">
            Your search, organized.
          </h1>
        </div>
        <p className="max-w-sm text-sm leading-6 text-[#665d55] sm:text-right">
          L is building the context it needs before it starts looking on your behalf.
        </p>
      </header>

      <div className="grid gap-px overflow-hidden border border-[#171310]/20 bg-[#171310]/20 md:grid-cols-3">
        {statusCards.map((card) => (
          <article key={card.code} className="bg-[#f7f3eb] p-5 sm:p-6">
            <div className="flex items-center justify-between text-[#806d60]">
              <span className="rule-label">{card.label}</span>
              <span className="font-mono text-xs">{card.code}</span>
            </div>
            <p className="mt-12 font-display text-3xl tracking-[-0.05em]">
              {card.value}
            </p>
            <p className="mt-3 text-sm leading-6 text-[#665d55]">{card.detail}</p>
          </article>
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.3fr_0.7fr]">
        <article className="paper-grain case-corners overflow-hidden border border-[#171310]/25 bg-[#1b1714] p-6 text-[#f7f2e8] sm:p-8">
          <div className="flex items-start justify-between gap-4 border-b border-white/20 pb-6">
            <div>
              <p className="rule-label text-[#d8c9b2]">Next action</p>
              <h2 className="mt-3 font-display text-4xl tracking-[-0.06em] sm:text-5xl">
                Give L your profile.
              </h2>
            </div>
            <Radar className="shrink-0 text-[#d8c9b2]" size={28} strokeWidth={1.4} />
          </div>

          <p className="mt-8 max-w-xl text-sm leading-7 text-[#d7cfc2] sm:text-base">
            Upload a resume or fill in your details yourself. You decide what L knows; it uses that context to judge future opportunities.
          </p>

          <Link
            href="/profile"
            className="mt-10 inline-flex items-center gap-3 border border-[#f7f2e8] bg-[#f7f2e8] px-5 py-3.5 text-sm font-semibold text-[#171310] transition hover:bg-transparent hover:text-[#f7f2e8]"
          >
            Open profile file <ArrowUpRight size={17} />
          </Link>
        </article>

        <article className="border border-[#171310]/20 bg-[#f7f3eb] p-6 sm:p-8">
          <div className="flex items-center justify-between">
            <p className="rule-label text-[#806d60]">System log</p>
            <Clock3 size={18} className="text-[#806d60]" />
          </div>
          <div className="mt-8 space-y-5">
            <LogItem icon={FilePenLine} text="Profile workspace is available." />
            <LogItem icon={Radar} text="Daily web discovery is planned next." />
            <LogItem icon={Send} text="Telegram delivery is not connected yet." />
          </div>
        </article>
      </div>
    </section>
  );
}

function LogItem({
  icon: Icon,
  text,
}: {
  icon: typeof FilePenLine;
  text: string;
}) {
  return (
    <div className="flex gap-3 border-b border-[#171310]/15 pb-5 text-sm leading-6 text-[#665d55] last:border-0 last:pb-0">
      <Icon size={17} className="mt-1 shrink-0 text-[#8d2030]" />
      <p>{text}</p>
    </div>
  );
}
