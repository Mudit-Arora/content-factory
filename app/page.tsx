import { Sparkles } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-surface via-[#0b1320] to-black">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center px-6 py-20 text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-slate-700/50 bg-white/5 px-4 py-2 text-sm text-slate-200">
          <Sparkles className="h-4 w-4 text-indigo-400" />
          AI Content Creator Platform
        </div>
        <h1 className="text-balance text-4xl font-semibold text-white sm:text-5xl">
          Create premium campaigns with a chat-first creative studio
        </h1>
        <p className="mt-4 max-w-2xl text-pretty text-lg text-slate-300">
          Research, strategize, and generate visuals in one focused workspace.
          Connect your MCP tools and ship content faster than ever.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="rounded-full bg-indigo-500 px-6 py-3 text-sm font-semibold text-white shadow-glow transition hover:bg-indigo-400"
          >
            Go to dashboard
          </Link>
          <button className="rounded-full border border-slate-700/70 px-6 py-3 text-sm font-semibold text-slate-200 transition hover:border-slate-500">
            View demo
          </button>
        </div>
      </div>
    </main>
  );
}
