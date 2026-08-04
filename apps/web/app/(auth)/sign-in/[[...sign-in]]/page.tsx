import { SignIn } from "@clerk/nextjs";

export default function Page() {
  return (
    <main className="grid min-h-screen lg:grid-cols-2">
      <section className="flex flex-col justify-center bg-black p-12 text-white">
        <h1 className="text-5xl font-bold">Welcome to L</h1>
        <p className="mt-4 text-zinc-400">Stop searching. Start applying.</p>
      </section>

      <section className="flex items-center justify-center">
        <SignIn />
      </section>
    </main>
  );
}
