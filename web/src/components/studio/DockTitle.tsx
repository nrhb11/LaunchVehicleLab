import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function DockTitle({
  title,
  children,
  className,
}: {
  title: string;
  children?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex h-7 shrink-0 items-center justify-between gap-2 border-b border-border bg-raised px-2",
        className,
      )}
    >
      <h2 className="text-micro font-medium uppercase tracking-[0.14em] text-subtle">{title}</h2>
      {children}
    </div>
  );
}
