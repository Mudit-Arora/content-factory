"use client";

import { MessageSquare, Plus, Search } from "lucide-react";
import { motion } from "framer-motion";

const sessions = [
  "December campaign",
  "Product launch ideas",
  "Influencer kit",
  "Q1 growth plan"
];

export default function Sidebar() {
  return (
    <aside className="flex h-full flex-col border-r border-slate-800 bg-panel/80 px-4 py-6">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-white">Sessions</div>
        <button className="rounded-full border border-slate-700/60 p-2 text-slate-200 transition hover:border-slate-500">
          <Plus className="h-4 w-4" />
        </button>
      </div>
      <div className="mt-5 flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2 text-xs text-slate-400">
        <Search className="h-4 w-4" />
        Search sessions
      </div>
      <div className="mt-6 flex-1 space-y-2 overflow-auto pr-1">
        {sessions.map((session, index) => (
          <motion.button
            whileHover={{ scale: 1.01 }}
            key={session}
            className={`flex w-full items-center gap-2 rounded-xl border px-3 py-3 text-left text-sm transition ${
              index === 0
                ? "border-indigo-400/50 bg-indigo-500/10 text-white"
                : "border-slate-800 bg-slate-900/40 text-slate-300"
            }`}
          >
            <MessageSquare className="h-4 w-4 text-indigo-300" />
            <span className="truncate">{session}</span>
          </motion.button>
        ))}
      </div>
    </aside>
  );
}
