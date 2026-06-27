import { cn } from "@/lib/utils";

export function Logo({
  className,
  size = "md",
  label = "Brand Name",
  iconSrc = "/logo_icon.svg",
  iconAlt = "brand logo",
}: {
  className?: string;
  size?: "sm" | "md" | "lg";
  label?: string;
  iconSrc?: string;
  iconAlt?: string;
}) {
  const sizes = { sm: "text-xl", md: "text-2xl", lg: "text-3xl" } as const;
  return (
    <div
      className={cn(
        "flex items-center gap-2 font-semibold tracking-tight text-white",
        sizes[size],
        className
      )}
    >
      <img src={iconSrc} alt={iconAlt} className="h-8 w-8" />
      <span>{label}</span>
    </div>
  );
}
