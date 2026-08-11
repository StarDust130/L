import { auth } from "@clerk/nextjs/server";
import TelegramPage from "../TelegramPage";

type Props = {
  searchParams: Promise<{
    token?: string;
  }>;
};

export default async function Telegram({ searchParams }: Props) {
  const { token } = await searchParams;

  if (!token) {
    return <div>Invalid Telegram link. 👎</div>;
  }

  const { isAuthenticated, redirectToSignIn } = await auth();

  if (!isAuthenticated) {
    return redirectToSignIn({
      returnBackUrl: `/telegram?token=${encodeURIComponent(token)}`,
    });
  }

  return <TelegramPage token={token} />;
}
