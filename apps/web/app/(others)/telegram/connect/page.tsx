import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

import TelegramPage from "../TelegramPage";

type TelegramPageProps = {
  searchParams: Promise<{
    token?: string;
  }>;
};

export default async function TelegramPageRoute({
  searchParams,
}: TelegramPageProps) {
  const { token } = await searchParams;

  // ❌ Telegram link is missing.
  if (!token) {
    return <div>Invalid Telegram connection link.</div>;
  }

  const { userId } = await auth();

  // 🔐 Not logged in → preserve token through login.
  if (!userId) {
    redirect(
      `/sign-in?redirect_url=${encodeURIComponent(`/telegram/connect?token=${token}`)}`,
    );
  }

  return <TelegramPage token={token} />;
}
