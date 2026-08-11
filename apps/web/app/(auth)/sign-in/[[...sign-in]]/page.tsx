import { SignIn } from "@clerk/nextjs";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

import { AuthFrame } from "../../../components/auth-frame";

type SignInPageProps = {
  searchParams: Promise<{
    redirect_url?: string;
  }>;
};

export default async function SignInPage({ searchParams }: SignInPageProps) {
  const { userId } = await auth();
  const { redirect_url } = await searchParams;

  // 🔐 Already logged in → continue to the requested page.
  if (userId) {
    redirect(redirect_url || "/dashboard");
  }

  return (
    <AuthFrame
      eyebrow="Restricted access"
      title="Return to the investigation."
      description="Your saved profile, career preferences, and future daily brief are waiting inside."
      index="01"
    >
      <p className="rule-label text-[#7c6f62]">Sign in to L</p>
      <h2 className="mt-3 font-display text-4xl tracking-[-0.055em] text-[#171310]">
        Good to see you.
      </h2>
      <p className="mt-3 text-sm leading-6 text-[#655d56]">
        Enter your details to continue your search.
      </p>

      <div className="mt-8">
        <SignIn
          forceRedirectUrl={redirect_url || "/dashboard"}
          signUpUrl="/sign-up"
          appearance={{
            variables: {
              colorPrimary: "#8d2030",
              colorBackground: "#f7f3eb",
              colorText: "#171310",
              borderRadius: "0px",
              fontFamily: '"Helvetica Neue", Arial, sans-serif',
            },
            elements: {
              card: "w-full border-0 bg-transparent p-0 shadow-none",
              header: "hidden",
              footer: "mt-6",
              formButtonPrimary:
                "bg-[#8d2030] shadow-none hover:bg-[#651522] focus:bg-[#651522]",
              formFieldInput:
                "border-[#171310]/25 bg-transparent shadow-none focus:border-[#8d2030]",
              socialButtonsBlockButton:
                "border-[#171310]/20 bg-transparent shadow-none hover:bg-[#ebe4d8]",
              footerActionLink: "text-[#8d2030] hover:text-[#651522]",
              identityPreviewEditButton: "text-[#8d2030]",
            },
          }}
        />
      </div>
    </AuthFrame>
  );
}
