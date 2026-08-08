// app/sections/Hero.tsx
"use client";

import React from "react";

export default function Hero() {
  return (
    <section className="relative w-full min-h-screen bg-[#14110f] text-[#F4EFE6] overflow-hidden">
      {/* Grain */}
      <div
        className="absolute inset-0 opacity-[0.025] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Nav */}
      <nav className="relative z-40 w-full px-8 md:px-16 py-8 flex justify-between items-start">
        <div className="flex flex-col">
          <div className="flex items-center justify-center">
            <span className="font-serif text-xl text-[#F4EFE6]">L</span>
            <span className="font-mono text-[9px] tracking-[0.35em] text-[rgba(244,239,230,0.4)] uppercase pl-9">
              Career Intelligence
            </span>
          </div>
        </div>
        <div className="flex items-center gap-10">
          <a
            href="#"
            className="font-mono text-[11px] tracking-[0.15em] text-[rgba(244,239,230,0.5)] hover:text-[#F4EFE6] transition-colors duration-300"
          >
            Sign in
          </a>
          <a
            href="#"
            className="font-mono text-[11px] tracking-[0.15em] text-[#F4EFE6] flex items-center gap-2 group"
          >
            Open case
            <ArrowUpRight />
          </a>
        </div>
      </nav>

      {/* Main */}
      <div className="relative z-30 max-w-[1400px] mx-auto px-8 md:px-16 pt-8 md:pt-16 pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-start">
          {/* LEFT */}
          <LeftColumn />

          {/* RIGHT: Dossier Stack */}
          <DossierStack />
        </div>
      </div>

      {/* Bottom */}
      <div className="absolute bottom-0 left-0 right-0 border-t border-[rgba(244,239,230,0.06)] py-5 px-8 md:px-16 flex justify-between items-center z-40">
        <span className="font-mono text-[9px] tracking-[0.3em] text-[rgba(244,239,230,0.25)] uppercase">
          L Intelligence Division
        </span>
        <div className="flex items-center gap-2">
          <div className="w-1 h-1 bg-[#A52D3F] rounded-full animate-pulse" />
          <span className="font-mono text-[9px] tracking-[0.2em] text-[rgba(244,239,230,0.25)] uppercase">
            System Online
          </span>
        </div>
      </div>

      {/* Fonts */}
      <style jsx global>{`
        @import url("https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=JetBrains+Mono:wght@300;400;500;600&display=swap");
        .font-serif {
          font-family: "Playfair Display", Georgia, serif;
        }
        .font-mono {
          font-family: "JetBrains Mono", monospace;
        }
      `}</style>
    </section>
  );
}

/* ─── Left Column ─── */

function LeftColumn() {
  return (
    <div className="flex flex-col gap-10 max-w-xl pt-4">
      {/* Badge */}
      <div className="flex items-center gap-3">
        <span className="w-1.5 h-1.5 rounded-full bg-[#A52D3F]" />
        <span className="font-mono text-[10px] tracking-[0.3em] text-[#A52D3F] uppercase">
          Your Private Career Intelligence System
        </span>
      </div>

      {/* Headline */}
      <h1 className="font-serif text-5xl md:text-6xl lg:text-[4.5rem] text-[#F4EFE6] leading-[1.05] tracking-[-0.02em]">
        Find the work
        <br />
        <span className="text-[#A52D3F]">worth</span>
        <br />
        <span className="text-[#A52D3F]">pursuing.</span>
      </h1>

      {/* Body */}
      <p className="text-[15px] leading-[1.7] text-[rgba(244,239,230,0.55)] max-w-sm">
        L reads the field, learns your profile, and delivers a focused daily
        brief of roles that deserve your attention.
      </p>

      {/* CTAs */}
      <div className="flex flex-wrap items-center gap-6 pt-2">
        <button className="group px-8 py-4 bg-[#F4EFE6] text-[#14110f] font-mono text-[11px] tracking-[0.2em] uppercase font-medium hover:bg-[#A52D3F] hover:text-[#F4EFE6] transition-all duration-500">
          <span className="flex items-center gap-3">
            Begin your case
            <ArrowUpRight />
          </span>
        </button>
        <a
          href="#"
          className="font-mono text-[11px] tracking-[0.15em] text-[rgba(244,239,230,0.5)] hover:text-[#F4EFE6] transition-colors duration-300 flex items-center gap-2 group"
        >
          Return to L
          <ArrowDownLeft />
        </a>
      </div>

      {/* Trust */}
      <div className="flex items-center gap-4 pt-6 border-t border-[rgba(244,239,230,0.06)]">
        <ShieldIcon />
        <span className="font-mono text-[9px] tracking-[0.2em] text-[rgba(244,239,230,0.3)] uppercase">
          Built for deliberate decisions.
        </span>
      </div>
    </div>
  );
}

/* ─── Dossier Stack ─── */

function DossierStack() {
  return (
    <div className="relative h-[520px] md:h-[600px] flex items-center justify-center lg:justify-end">
      {/* Back card */}
      <div className="absolute w-[90%] md:w-[420px] h-[420px] md:h-[480px] bg-[#1a1614] border border-[rgba(244,239,230,0.06)] transform rotate-[2deg] translate-x-4 translate-y-4" />

      {/* Middle card */}
      <div className="absolute w-[90%] md:w-[420px] h-[420px] md:h-[480px] bg-[#EEE7D8] text-[#1a1614] transform rotate-[-1deg] translate-x-2 translate-y-2 shadow-2xl">
        <div className="p-8 h-full flex flex-col">
          <div className="flex justify-between items-start mb-8">
            <span className="font-mono text-[9px] tracking-[0.3em] text-[rgba(26,22,20,0.4)] uppercase">
              Intel / 002
            </span>
            <span className="font-mono text-[8px] tracking-[0.15em] text-[#A52D3F] uppercase border border-[#A52D3F] px-2 py-1">
              Verified
            </span>
          </div>
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-24 h-24 mx-auto border border-[rgba(26,22,20,0.1)] rounded-full flex items-center justify-center mb-4">
                <span className="font-serif text-5xl text-[#A52D3F]">L</span>
              </div>
              <p className="font-serif text-lg text-[rgba(26,22,20,0.7)]">
                Daily Brief Ready
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Front card */}

      <div className="card-front relative w-[90%] md:w-[400px] h-[400px] md:h-[460px] bg-[#F4EFE6] text-[#1a1614] shadow-2xl z-10 transition-all duration-700 hover:-translate-y-2 hover:shadow-[0_20px_60px_rgba(0,0,0,0.4)] cursor-pointer group">
        <CornerMarks />
        <div className="p-8 md:p-10 h-full flex flex-col">
          {/* Header */}
          <div className="flex justify-between items-start mb-8">
            <div className="flex flex-col gap-1">
              <span className="font-mono text-[9px] tracking-[0.3em] text-[rgba(26,22,20,0.35)] uppercase">
                Case File / 001
              </span>
              <span className="font-serif text-xl text-[#1a1614]">
                Opportunity Brief
              </span>
            </div>
            <div className="w-8 h-8 rounded-full border border-[rgba(26,22,20,0.12)] flex items-center justify-center group-hover:border-[#A52D3F] group-hover:bg-[#A52D3F]/10 transition-all duration-500">
              <div className="w-2 h-2 rounded-full bg-[#A52D3F] group-hover:scale-125 transition-transform duration-300" />
            </div>
          </div>

          {/* Photo */}
          <div className="flex-1 relative mb-6 overflow-hidden bg-[rgba(26,22,20,0.03)]">
            <img
              src="https://i.pinimg.com/736x/6e/83/9e/6e839e2b8e85ca0eb0b977ebe559360a.jpg"
              alt="Subject"
              className="w-full h-full object-cover object-top opacity-70 grayscale group-hover:grayscale-0 group-hover:opacity-100 group-hover:scale-105 transition-all duration-700"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#F4EFE6] via-transparent to-transparent opacity-40" />
            <div className="absolute bottom-3 left-3 transform translate-y-2 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-500">
              <span className="font-mono text-[7px] tracking-[0.2em] text-[rgba(26,22,20,0.6)] uppercase bg-[#F4EFE6] px-2 py-1">
                Subject Photograph
              </span>
            </div>
          </div>

          {/* Data */}
          <div className="space-y-3">
            <DataRow label="Signal Status" value="Active" />
            <DataRow label="Profile" value="Classified" />
            <DataRow label="Delivery" value="Daily Brief" highlight />
          </div>

          {/* Footer */}
          <div className="mt-auto pt-5 flex justify-between items-end">
            <span className="font-mono text-[8px] tracking-[0.2em] text-[rgba(26,22,20,0.3)] uppercase">
              Ref: L-2026-001-X
            </span>
            <div className="border border-[#A52D3F] px-3 py-1 transform rotate-[-3deg] group-hover:rotate-[-5deg] group-hover:scale-110 transition-all duration-300">
              <span className="font-mono text-[8px] tracking-[0.15em] text-[#A52D3F] uppercase">
                Eyes Only
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Floating annotation */}
      <div className="absolute -right-4 top-1/4 hidden xl:block">
        <div className="bg-[#14110f] border border-[rgba(165,45,63,0.2)] px-4 py-3 transform rotate-[4deg]">
          <p className="font-mono text-[20px] text-[#A52D3F] font-bold">96%</p>
          <p className="font-mono text-[8px] tracking-[0.2em] text-[rgba(244,239,230,0.35)] uppercase mt-1">
            Match Score
          </p>
        </div>
      </div>
    </div>
  );
}

/* ─── Sub-Components ─── */

function CornerMarks() {
  return (
    <>
      <div className="absolute top-4 left-4 w-5 h-5 border-t border-l border-[rgba(26,22,20,0.15)]" />
      <div className="absolute top-4 right-4 w-5 h-5 border-t border-r border-[rgba(26,22,20,0.15)]" />
      <div className="absolute bottom-4 left-4 w-5 h-5 border-b border-l border-[rgba(26,22,20,0.15)]" />
      <div className="absolute bottom-4 right-4 w-5 h-5 border-b border-r border-[rgba(26,22,20,0.15)]" />
    </>
  );
}

function DataRow({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="flex justify-between items-center pb-3 border-b border-[rgba(26,22,20,0.08)] last:border-0 last:pb-0">
      <span className="font-mono text-[10px] tracking-[0.15em] text-[rgba(26,22,20,0.4)] uppercase">
        {label}
      </span>
      <span
        className={`font-mono text-[10px] tracking-[0.15em] uppercase font-medium ${highlight ? "text-[#A52D3F]" : "text-[#1a1614]"}`}
      >
        {value}
      </span>
    </div>
  );
}

function ArrowUpRight() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform"
    >
      <path
        d="M1 11L11 1M11 1H3M11 1V9"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
  );
}

function ArrowDownLeft() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      className="group-hover:-translate-x-0.5 group-hover:translate-y-0.5 transition-transform"
    >
      <path
        d="M11 1L1 11M1 11H9M1 11V3"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 14 14"
      fill="none"
      className="text-[rgba(244,239,230,0.3)]"
    >
      <path
        d="M7 1L8.5 5.5H13L9.5 8L10.5 12.5L7 10L3.5 12.5L4.5 8L1 5.5H5.5L7 1Z"
        stroke="currentColor"
        strokeWidth="1"
      />
    </svg>
  );
}
