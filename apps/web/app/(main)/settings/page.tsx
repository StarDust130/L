import TelegramConnect from "@/app/components/service/TelegramConnect";
import { auth } from "@clerk/nextjs/server";

export default async function SettingsPage() {
  await auth.protect();

  return <div className="flex flex-col">Settings <TelegramConnect /></div>;
}
