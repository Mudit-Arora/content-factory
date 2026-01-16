import Sidebar from "../../components/Sidebar";
import Chat from "../../components/chat/Chat";

export default function DashboardPage() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-surface text-slate-100">
      <div className="hidden w-72 border-r border-slate-800 lg:block">
        <Sidebar />
      </div>
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-800 bg-panel/70 px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
              Dashboard
            </p>
            <h1 className="text-lg font-semibold text-white">
              AI Content Creator Studio
            </h1>
          </div>
          <div className="rounded-full border border-slate-700/70 bg-slate-900/60 px-4 py-2 text-xs text-slate-300">
            MCP Host: local server ready
          </div>
        </header>
        <main className="flex-1 overflow-hidden">
          <Chat />
        </main>
      </div>
    </div>
  );
}
