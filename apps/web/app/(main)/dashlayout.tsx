"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";
import {
  BriefcaseBusiness,
  ChartArea,
  FileSearch,
  Menu,
  Settings2,
  ShieldCheck,
  X,
} from "lucide-react";
import type { ReactNode } from "react";
import { useState } from "react";

import { BrandMark } from "../components/brand-mark";

type DashboardLayoutProps = {
  children: ReactNode;
};

const navigation = [
  {
    href: "/dashboard",
    label: "Overview",
    icon: BriefcaseBusiness,
    code: "01",
  },
  {
    href: "/chat",
    label: "Chat",
    icon: ChartArea,
    code: "02",
  },
  {
    href: "/profile",
    label: "Profile file",
    icon: FileSearch,
    code: "02",
  },
  {
    href: "/settings",
    label: "Settings",
    icon: Settings2,
    code: "03",
  },
];

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#e9e3d8] text-[#171310] lg:grid lg:grid-cols-[17.5rem_minmax(0,1fr)]">
      <aside className="paper-grain fixed inset-y-0 left-0 z-30 hidden w-[17.5rem] flex-col border-r border-[#171310]/25 bg-[#1b1714] p-5 text-[#f7f2e8] lg:flex">
        <SidebarContent />
      </aside>

      <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-[#171310]/15 bg-[#f6f1e8]/95 px-4 backdrop-blur lg:hidden">
        <BrandMark />
        <button
          type="button"
          className="grid size-10 place-items-center border border-[#171310]/20"
          onClick={() => setIsMobileNavOpen(true)}
          aria-label="Open navigation"
        >
          <Menu size={19} />
        </button>
      </header>

      {isMobileNavOpen ? (
        <div className="fixed inset-0 z-50 bg-[#171310]/70 p-3 lg:hidden">
          <aside className="paper-grain flex h-full w-full max-w-sm flex-col border border-white/25 bg-[#1b1714] p-5 text-[#f7f2e8] shadow-2xl">
            <div className="flex justify-end">
              <button
                type="button"
                className="grid size-10 place-items-center border border-white/25"
                onClick={() => setIsMobileNavOpen(false)}
                aria-label="Close navigation"
              >
                <X size={19} />
              </button>
            </div>
            <SidebarContent onNavigate={() => setIsMobileNavOpen(false)} />
          </aside>
        </div>
      ) : null}

      <main className="min-w-0 lg:col-start-2">
        <div className="mx-auto min-h-screen max-w-[94rem] px-4 py-5 sm:px-7 sm:py-8 lg:px-10">
          {children}
        </div>
      </main>
    </div>
  );
}

type SidebarContentProps = {
  onNavigate?: () => void;
};

function SidebarContent({ onNavigate }: SidebarContentProps) {
  const pathname = usePathname();

  return (
    <>
      <div className="flex items-center mb-10 justify-between">
        <BrandMark inverted />
        <span className="rule-label text-white/45">v1.0</span>
      </div>



      <nav className="mt-6 space-y-1" aria-label="Main navigation">
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={`group flex items-center gap-3 border px-3 py-3 text-sm transition ${
                isActive
                  ? "border-[#d8c9b2] bg-[#f7f2e8] text-[#171310]"
                  : "border-transparent text-white/65 hover:border-white/25 hover:text-white"
              }`}
              aria-current={isActive ? "page" : undefined}
            >
              <span className="font-mono text-[0.65rem] opacity-60">{item.code}</span>
              <Icon size={17} strokeWidth={1.7} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto space-y-5 border-t border-white/15 pt-5">
        <div className="flex items-center gap-3 text-xs leading-5 text-white/55">
          <ShieldCheck size={16} className="shrink-0 text-[#d8c9b2]" />
          <span>Your profile is private to your account.</span>
        </div>
        <div className="flex items-center justify-between border-t border-white/15 pt-4">
          <span className="rule-label text-white/45">Account</span>
          <UserButton
            appearance={{
              elements: {
                avatarBox: "size-8 rounded-none",
              },
            }}
          />
        </div>
      </div>
    </>
  );
}
