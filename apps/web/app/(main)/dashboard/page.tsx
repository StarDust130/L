import Link from "next/link";
import {
  ArrowUpRight,
  Clock3,
  FilePenLine,
  Gauge,
  Radar,
  Send,
  Sparkles,
} from "lucide-react";

const statusCards = [
  {
    label: "Profile signal",
    value: "Ready for review",
    detail: "Keep your preferences accurate.",
    code: "01",
    icon: FilePenLine,
    state: "Ready",
  },
  {
    label: "Daily brief",
    value: "Not scheduled",
    detail: "Telegram delivery arrives in a later phase.",
    code: "02",
    icon: Send,
    state: "Queued",
  },
  {
    label: "Job sources",
    value: "Field not active",
    detail: "Discovery starts when the agent is built.",
    code: "03",
    icon: Radar,
    state: "Pending",
  },
];

export default function DashboardPage() {
  return (
    <section className="space-y-5 sm:space-y-7">
      <header className="flex flex-col gap-6 border-b border-[#171310]/15 pb-7 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-[#8d2030]">
            <Sparkles size={15} strokeWidth={1.8} />
            <p className="rule-label">Morning brief</p>
          </div>
          <h1 className="mt-3 max-w-3xl font-display text-5xl leading-[0.95] tracking-[-0.065em] sm:text-7xl">
            Make room for the right work.
          </h1>
        </div>
        <div className="flex max-w-sm items-start gap-3 text-sm leading-6 text-[#665d55] sm:text-right">
          <Gauge size={18} className="mt-1 hidden shrink-0 text-[#8d2030] sm:block" />
          <p>L is building the context it needs before it starts looking on your behalf.</p>
        </div>
      </header>

      <div className="grid gap-px overflow-hidden border border-[#171310]/20 bg-[#171310]/20 md:grid-cols-3">
        {statusCards.map((card) => (
          <article key={card.code} className="group bg-[#f7f3eb] p-5 transition-colors hover:bg-[#fbf8f1] sm:p-6">
            <div className="flex items-center justify-between text-[#806d60]">
              <div className="flex items-center gap-2">
                <card.icon size={16} strokeWidth={1.6} />
                <span className="rule-label">{card.label}</span>
              </div>
              <span className="font-mono text-xs">{card.code}</span>
            </div>
            <div className="mt-12 flex items-end justify-between gap-3">
              <p className="font-display text-3xl tracking-[-0.05em]">
                {card.value}
              </p>
              <span className="mb-1 text-[0.65rem] uppercase tracking-[0.16em] text-[#8d2030]">{card.state}</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-[#665d55]">{card.detail}</p>
          </article>
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.3fr_0.7fr]">
        <article className="paper-grain case-corners overflow-hidden border border-[#171310]/25 bg-[#1b1714] p-6 text-[#f7f2e8] sm:p-8">
          <div className="flex items-start justify-between gap-4 border-b border-white/20 pb-6">
            <div>
              <p className="rule-label text-[#d8c9b2]">Next action</p>
              <h2 className="mt-3 max-w-lg font-display text-4xl leading-none tracking-[-0.06em] sm:text-5xl">
                Start with the context only you can give.
              </h2>
            </div>
            <Radar className="shrink-0 text-[#d8c9b2]" size={28} strokeWidth={1.4} />
          </div>

          <p className="mt-8 max-w-xl text-sm leading-7 text-[#d7cfc2] sm:text-base">
            Upload a resume or fill in your details yourself. Your profile becomes the lens L uses to judge future opportunities.
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
