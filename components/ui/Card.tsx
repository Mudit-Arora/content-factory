import type { ReactNode } from "react";

export default function Card({
  children,
  title
}: {
  children: ReactNode;
  title?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg">
      {title ? (
        <div className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          {title}
        </div>
      ) : null}
      {children}
    </div>
  );
}
