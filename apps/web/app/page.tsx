import Link from "next/link";
import { ArrowDownRight, ArrowUpRight, CircleDot, ShieldCheck } from "lucide-react";

import { BrandMark } from "./components/brand-mark";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#171310] p-3 text-[#f7f2e8] sm:p-5">
      <section className="paper-grain case-corners relative flex min-h-[calc(100vh-1.5rem)] flex-col overflow-hidden border border-white/20 bg-[#1c1714] sm:min-h-[calc(100vh-2.5rem)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_81%_20%,rgba(141,32,48,0.47),transparent_22rem),radial-gradient(circle_at_20%_80%,rgba(225,215,193,0.09),transparent_26rem)]" />

        <nav className="relative z-10 flex items-center justify-between border-b border-white/15 px-5 py-5 sm:px-8">
          <BrandMark inverted />
          <div className="flex items-center gap-3 text-sm">
            <Link
              href="/sign-in"
              className="hidden text-white/70 transition hover:text-white sm:inline"
            >
              Sign in
            </Link>
            <Link
              href="/sign-up"
              className="inline-flex items-center gap-2 border border-white/35 px-4 py-2.5 font-medium transition hover:bg-[#f7f2e8] hover:text-[#171310]"
            >
              Open case <ArrowUpRight size={15} />
            </Link>
          </div>
        </nav>

        <div className="relative z-10 mx-auto grid w-full max-w-7xl flex-1 items-center gap-12 px-5 py-16 sm:px-8 lg:grid-cols-[1.08fr_0.92fr] lg:py-20">
          <div>
            <div className="rule-label flex items-center gap-3 text-[#d9cdb9]">
              <span className="size-2 rounded-full bg-[#b43647] shadow-[0_0_0_4px_rgba(180,54,71,0.18)]" />
              Your private career intelligence system
            </div>

            <h1 className="mt-8 max-w-4xl font-display text-6xl leading-[0.83] tracking-[-0.075em] sm:text-7xl md:text-8xl lg:text-9xl">
              Find the work
              <span className="block text-[#b43647]">worth pursuing.</span>
            </h1>

            <p className="mt-8 max-w-xl text-base leading-7 text-[#d7cfc2] sm:text-lg">
              L reads the field, learns your profile, and delivers a focused daily brief of roles that deserve your attention.
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link
                href="/sign-up"
                className="inline-flex items-center gap-3 bg-[#f7f2e8] px-5 py-3.5 text-sm font-semibold text-[#171310] transition hover:bg-[#d9cdb9]"
              >
                Begin your case <ArrowUpRight size={17} />
              </Link>
              <Link
                href="/sign-in"
                className="inline-flex items-center gap-3 px-2 py-3 text-sm text-white/70 transition hover:text-white"
              >
                Return to L <ArrowDownRight size={17} />
              </Link>
            </div>
          </div>

          <div className="mx-auto w-full max-w-md lg:mr-0">
            <div className="relative border border-white/35 bg-[#e9e2d5] p-3 text-[#171310] shadow-[12px_12px_0_rgba(141,32,48,0.5)] sm:p-5">
              <div className="case-corners paper-grain min-h-[29rem] border border-[#171310]/50 p-6 sm:min-h-[33rem] sm:p-8">
                <div className="flex items-start justify-between border-b border-[#171310]/25 pb-5">
                  <div>
                    <p className="rule-label text-[#715f53]">Case file / 001</p>
                    <p className="mt-2 font-display text-3xl tracking-[-0.05em]">Opportunity brief</p>
                  </div>
                  <CircleDot size={26} strokeWidth={1.4} />
                </div>

                <div className="mt-10 flex justify-center">
                  <div className="grid size-32 place-items-center rounded-full border border-[#171310] p-3 sm:size-40">
                    <div className="grid size-full place-items-center rounded-full border border-[#171310]">
                      <span className="font-display text-6xl italic text-[#8d2030] sm:text-7xl">L</span>
                    </div>
                  </div>
                </div>

                <div className="mt-10 space-y-4 text-sm">
                  <div className="flex justify-between border-b border-[#171310]/20 pb-3">
                    <span className="text-[#715f53]">Signal status</span>
                    <span className="font-mono text-xs font-semibold">STANDBY</span>
                  </div>
                  <div className="flex justify-between border-b border-[#171310]/20 pb-3">
                    <span className="text-[#715f53]">Profile</span>
                    <span className="font-mono text-xs font-semibold">PRIVATE</span>
                  </div>
                  <div className="flex justify-between border-b border-[#171310]/20 pb-3">
                    <span className="text-[#715f53]">Delivery</span>
                    <span className="font-mono text-xs font-semibold">DAILY BRIEF</span>
                  </div>
                </div>

                <div className="mt-9 flex items-center gap-3 text-xs text-[#715f53]">
                  <ShieldCheck size={16} />
                  Built for deliberate decisions.
                </div>
              </div>
            </div>
          </div>
        </div>

        <footer className="relative z-10 flex flex-col gap-5 border-t border-white/15 px-5 py-5 text-xs text-white/55 sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <span className="font-mono">L / CAREER INTELLIGENCE / 2026</span>
          <span>Private by default. Intentional by design.</span>
        </footer>
      </section>
    </main>
  );
}
