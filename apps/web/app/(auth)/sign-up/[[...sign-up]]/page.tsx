import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { SignUp } from "@clerk/nextjs";

export default async function SignUpPage() {
  const { userId } = await auth();

  if (userId) {
    redirect("/dashboard");
  }
  
  return (
    <main className="grid min-h-screen lg:grid-cols-2">
      {/* Left Side */}
      <section className="hidden lg:flex flex-col justify-center bg-black p-12 text-white">
        <h1 className="text-5xl font-bold">Join L</h1>

        <p className="mt-4 max-w-md text-zinc-400 text-lg">
          Your AI career agent that helps you discover opportunities, understand
          your strengths, and land your next role faster.
        </p>

        <div className="mt-10 space-y-4 text-zinc-300">
          <p>🤖 AI-powered job discovery</p>
          <p>🎯 Personalized career recommendations</p>
          <p>📱 Daily opportunity updates</p>
        </div>
      </section>

      {/* Right Side */}
      <section className="flex items-center justify-center p-6">
        <SignUp />
      </section>
    </main>
  );
}
