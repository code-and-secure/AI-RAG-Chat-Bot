import { useState } from "react";
import { activatePublicBot } from "../api";
import type { BotState, PublicBotType, Session } from "../types";

const BOTS: { type: PublicBotType; icon: string; title: string; desc: string }[] = [
  {
    type: "finance",
    icon: "📈",
    title: "FinanceAI",
    desc: "Preloaded with Tesla (TSLA) Q4 2025 financial statements. Check revenues, margins, and Cybertruck deliveries.",
  },
  {
    type: "hr",
    icon: "👥",
    title: "HR Policy Advisor",
    desc: "Know your employee rights. Pre-trained with corporate policy on health insurance, PTO days, and remote work.",
  },
  {
    type: "legal",
    icon: "⚖️",
    title: "Legal NDA Advisor",
    desc: "Check contract clauses instantly. Preloaded with standard Non-Disclosure Agreement templates.",
  },
];

interface Props {
  onActivate: (s: Session) => void;
  setBotState: (s: BotState) => void;
}

export default function PublicBotsPage({ onActivate, setBotState }: Props) {
  const [loading, setLoading] = useState<PublicBotType | null>(null);
  const [error, setError] = useState("");

  async function activate(type: PublicBotType) {
    setLoading(type);
    setError("");
    setBotState("processing");
    try {
      const res = await activatePublicBot(type);
      onActivate({ id: res.session_id, name: res.name, chunks: res.chunks });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Activation failed");
      setBotState("idle");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">
          Choose a Pre-Configured <span className="text-blue-600 dark:text-blue-400">Assistant</span>
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">
          Instantly chat with preloaded domain-specific assistants — no file upload needed.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-300 rounded-xl px-4 py-3 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {BOTS.map((bot) => (
          <div key={bot.type} className="card flex flex-col gap-4">
            <div className="text-4xl">{bot.icon}</div>
            <div>
              <h3 className="font-bold text-gray-900 dark:text-white text-lg">{bot.title}</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">{bot.desc}</p>
            </div>
            <button
              onClick={() => activate(bot.type)}
              disabled={loading !== null}
              className="btn-primary mt-auto"
            >
              {loading === bot.type ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Configuring…
                </span>
              ) : (
                `Activate ${bot.title}`
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
