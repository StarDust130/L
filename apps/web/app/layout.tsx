import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";

import "./globals.css";

export const metadata: Metadata = {
  title: "L: Career Intelligence",
  description:
    "L is a personal AI career agent for focused opportunity discovery.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="min-h-full">
      <body className="min-h-full">
        <ClerkProvider>{children}</ClerkProvider>
      </body>
    </html>
  );
}
