import { useRef, useState } from "react";
import { uploadDocument, sendChat, deleteSession } from "../api";
import type { BotState, ChatMessage, Session } from "../types";

interface Props {
  session: Session | null;
  chatHistory: ChatMessage[];
  setChatHistory: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  setBotState: (s: BotState) => void;
  onSessionStart: (s: Session) => void;
  onSessionClear: () => void;
}

export default function ChatPage({
  session,
  chatHistory,
  setChatHistory,
  setBotState,
  onSessionStart,
  onSessionClear,
}: Props) {
  const [query, setQuery] = useState("");
  const [uploading, setUploading] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [searchingWeb, setSearchingWeb] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setUploading(true);
    setBotState("processing");
    try {
      const res = await uploadDocument(file);
      onSessionStart({ id: res.session_id, name: res.filename, chunks: res.chunks });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setBotState("idle");
    } finally {
      setUploading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim() || thinking) return;
    const q = query.trim();
    setQuery("");
    setError("");
    setThinking(true);
    setSearchingWeb(false);
    setBotState("processing");
    try {
      const res = await sendChat(session?.id ?? null, q);
      if (res.used_web) setSearchingWeb(true);
      setChatHistory((prev) => [
        ...prev,
        { question: q, answer: res.answer, usedWeb: res.used_web },
      ]);
      setBotState(session ? "aside" : "idle");
      setTimeout(() => {
        setSearchingWeb(false);
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 2000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setBotState(session ? "aside" : "idle");
    } finally {
      setThinking(false);
    }
  }

  async function handleClose() {
    if (session) await deleteSession(session.id);
    onSessionClear();
  }

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-6 bg-gradient-to-br from-blue-600 to-indigo-700 dark:from-gray-800 dark:to-gray-900 rounded-2xl p-8 border border-blue-500/30 dark:border-gray-700">
        <div className="flex-1">
          <h1 className="text-3xl md:text-4xl font-extrabold text-white leading-tight">
            Empower Your Future with{" "}
            <span className="text-yellow-300 dark:text-blue-400">Vaultix</span>
          </h1>
          <p className="mt-3 text-blue-100 dark:text-gray-400 max-w-xl">
            Upload enterprise documents and instantly chat with your private data using
            precision-engineered AI.
          </p>
          <button onClick={() => fileRef.current?.click()} className="mt-5 bg-white text-blue-700 hover:bg-blue-50 font-semibold px-5 py-2.5 rounded-xl transition-colors dark:bg-blue-600 dark:text-white dark:hover:bg-blue-500">
            Get Started
          </button>
        </div>
        {/* Avatar — contained with matching rounded card */}
        <div className="w-44 md:w-52 shrink-0 rounded-2xl overflow-hidden ring-2 ring-white/20 shadow-2xl hidden md:block">
          <img
            src="/robot.png"
            alt="Vaultix AI"
            className="w-full h-full object-cover"
            onError={(e) => ((e.currentTarget as HTMLImageElement).style.display = "none")}
          />
        </div>
      </div>

      {/* File upload / active doc */}
      {!session ? (
        <div
          className="border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 rounded-2xl p-8 text-center cursor-pointer transition-colors bg-white dark:bg-transparent"
          onClick={() => fileRef.current?.click()}
        >
          <div className="text-4xl mb-3">📤</div>
          <p className="text-gray-700 dark:text-gray-300 font-medium">Upload PDF, TXT, DOCX</p>
          <p className="text-gray-400 text-sm mt-1">200 MB per file</p>
          {uploading && (
            <p className="mt-3 text-blue-500 text-sm animate-pulse">
              ⚙️ Analyzing document &amp; building vector index…
            </p>
          )}
          <input ref={fileRef} type="file" accept=".pdf,.txt,.docx" className="hidden" onChange={handleFileChange} />
        </div>
      ) : (
        <div className="flex items-center gap-4 bg-white dark:bg-gray-800 border-l-4 border-blue-500 rounded-2xl px-5 py-4 shadow-sm">
          <span className="text-3xl">📄</span>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-gray-900 dark:text-white truncate">{session.name}</p>
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              Securely indexed · <b>{session.chunks}</b> semantic chunks ready
            </p>
          </div>
          <span className="shrink-0 bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 text-xs font-bold px-3 py-1 rounded-full">
            🟢 ACTIVE
          </span>
          <button onClick={handleClose} className="shrink-0 btn-secondary text-sm">
            Close
          </button>
        </div>
      )}

      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-300 rounded-xl px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {/* Chat input */}
      {/* Sea-of-knowledge banner */}
      {searchingWeb && (
        <div className="flex items-center gap-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl px-4 py-3 text-blue-700 dark:text-blue-300 text-sm animate-pulse">
          <span className="text-xl">🌊</span>
          <span>Your vault is silent on this one — breaching the open web to surface your answer…</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          className="input flex-1"
          placeholder="Ask Vaultix anything… 📎"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={thinking}
        />
        <button type="submit" className="btn-primary px-6" disabled={thinking || !query.trim()}>
          {thinking ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Thinking
            </span>
          ) : (
            "Send"
          )}
        </button>
      </form>

      {/* Chat history */}
      {chatHistory.length > 0 && (
        <div className="space-y-6 mt-2">
          <hr className="border-gray-200 dark:border-gray-700" />
          {[...chatHistory].reverse().map((msg, i) => (
            <div key={i} className="space-y-2">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-xs text-white font-bold shrink-0">
                  You
                </div>
                <p className="text-gray-800 dark:text-gray-200 pt-1">{msg.question}</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center text-sm shrink-0">
                  🔷
                </div>
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-5 py-4 text-gray-800 dark:text-gray-200 text-sm leading-relaxed whitespace-pre-wrap flex-1 shadow-sm">
                  {msg.usedWeb && (
                    <span className="inline-flex items-center gap-1 mb-3 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs px-2.5 py-1 rounded-full border border-blue-200 dark:border-blue-700">
                      🌊 Sourced from the web
                    </span>
                  )}
                  <div>{msg.answer}</div>
                </div>
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}
