import { auth } from "@clerk/nextjs/server";

export default async function ProfilePage() {
  await auth.protect();

  return <div>Profile page</div>;
}
