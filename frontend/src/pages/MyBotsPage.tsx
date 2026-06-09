import { useEffect, useState } from "react";
import { fetchStats } from "../api";
import type { Session, Stats } from "../types";

interface Props {
  session: Session | null;
  onGoToChat: () => void;
}

export default function MyBotsPage({ session, onGoToChat }: Props) {
  const [stats, setStats] = useState<Stats>({ total_queries: 0, total_docs: 0, total_bots: 0 });

  useEffect(() => {
    fetchStats().then(setStats).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">
          Your Personal <span className="text-blue-600 dark:text-blue-400">Bots</span> Library
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">Manage your AI assistants and uploaded documents.</p>
      </div>

      {session ? (
        <div className="card flex items-center gap-4">
          <span className="text-3xl">✅</span>
          <div className="flex-1">
            <p className="font-semibold text-gray-900 dark:text-white">{session.name}</p>
            <p className="text-gray-500 dark:text-gray-400 text-sm">{session.chunks} chunks indexed</p>
          </div>
          <button onClick={onGoToChat} className="btn-primary text-sm">
            💬 Chat with this Bot
          </button>
        </div>
      ) : (
        <div className="card text-center py-10 text-gray-500 dark:text-gray-400">
          <p className="text-4xl mb-3">🤖</p>
          <p>No active bot. Head to <strong>Chat</strong> to upload a document and create one!</p>
        </div>
      )}

      <hr className="border-gray-200 dark:border-gray-800" />

      <div>
        <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Bot Statistics</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { icon: "🤖", label: "Total Custom Bots", value: stats.total_bots },
            { icon: "💬", label: "Total Queries Answered", value: stats.total_queries },
            { icon: "📄", label: "Total Documents Indexed", value: stats.total_docs },
          ].map((s) => (
            <div key={s.label} className="card text-center">
              <div className="text-4xl mb-2">{s.icon}</div>
              <div className="text-gray-500 dark:text-gray-400 text-sm mb-1">{s.label}</div>
              <div className="text-5xl font-extrabold text-blue-600 dark:text-blue-400">{s.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
