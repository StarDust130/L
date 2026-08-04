import { SignUp } from "@clerk/nextjs";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

import { AuthFrame } from "../../../components/auth-frame";

export default async function SignUpPage() {
  const { userId } = await auth();

  if (userId) {
    redirect("/dashboard");
  }

  return (
    <AuthFrame
      eyebrow="New case"
      title="Make your career search intentional."
      description="Give L your profile once. It will become the lens for every opportunity we find together."
      index="02"
    >
      <p className="rule-label text-[#7c6f62]">Create your account</p>
      <h2 className="mt-3 font-display text-4xl tracking-[-0.055em] text-[#171310]">
        Start your file.
      </h2>
      <p className="mt-3 text-sm leading-6 text-[#655d56]">
        A few minutes now saves hours of searching later.
      </p>

      <div className="mt-8">
        <SignUp
          signInUrl="/sign-in"
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
