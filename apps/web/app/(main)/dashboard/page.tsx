import { auth } from "@clerk/nextjs/server";

export default async function DashboardPage() {
  await auth.protect();

  return <div>Dashboard</div>;
}
