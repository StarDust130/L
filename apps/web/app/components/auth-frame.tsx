import type { ReactNode } from "react";

import { BrandMark } from "./brand-mark";

type AuthFrameProps = {
  children: ReactNode;
  eyebrow: string;
  title: string;
  description: string;
  index: string;
};

export function AuthFrame({
  children,
  eyebrow,
  title,
  description,
  index,
}: AuthFrameProps) {
  return (
    <main className="min-h-screen bg-[#171310] p-3 sm:p-5">
      <div className="grid min-h-[calc(100vh-1.5rem)] overflow-hidden border border-white/20 bg-[#efe9dd] lg:grid-cols-[0.9fr_1.1fr] sm:min-h-[calc(100vh-2.5rem)]">
        <section className="paper-grain case-corners relative flex min-h-[22rem] flex-col justify-between overflow-hidden bg-[#1c1714] p-7 text-[#f7f2e8] sm:p-10 lg:min-h-full">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_76%_31%,rgba(141,32,48,0.44),transparent_17rem)]" />
          <div className="relative z-10 flex items-center justify-between">
            <BrandMark inverted />
            <span className="rule-label text-white/55">file {index}</span>
          </div>

          <div className="relative z-10 py-10 lg:py-0">
            <p className="rule-label text-[#d7c9b2]">{eyebrow}</p>
            <h1 className="mt-5 max-w-md font-display text-5xl leading-[0.88] tracking-[-0.065em] sm:text-7xl">
              {title}
            </h1>
            <p className="mt-7 max-w-sm text-sm leading-6 text-[#d7cfc2] sm:text-base">
              {description}
            </p>
          </div>

          <div className="relative z-10 flex items-end justify-between border-t border-white/20 pt-5 text-xs text-white/55">
            <span className="font-mono">L / PRIVATE SYSTEM</span>
            <span>01-03</span>
          </div>
        </section>

        <section className="flex items-center justify-center bg-[#f7f3eb] p-6 sm:p-10 lg:p-16">
          <div className="w-full max-w-md">{children}</div>
        </section>
      </div>
    </main>
  );
}
