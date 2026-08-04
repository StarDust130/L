import { auth } from "@clerk/nextjs/server";
import type { ReactNode } from "react";

import DashboardLayout from "./dashlayout";

export default async function MainLayout({
  children,
}: {
  children: ReactNode;
}) {
  await auth.protect();

  return <DashboardLayout>{children}</DashboardLayout>;
}
