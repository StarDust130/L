import Link from "next/link";

type BrandMarkProps = {
  href?: string;
  inverted?: boolean;
};

export function BrandMark({
  href = "/",
  inverted = false,
}: BrandMarkProps) {
  const textColor = inverted ? "text-[#f7f2e8]" : "text-[#161310]";


  return (
    <Link
      href={href}
      className={`group inline-flex items-center gap-3 ${textColor}`}
      aria-label="L home"
    >
  
      <span className="leading-none">
        <span className="block font-display text-xl tracking-[-0.06em]">L</span>
        <span className="rule-label mt-1 block opacity-70">career intelligence</span>
      </span>
    </Link>
  );
}
