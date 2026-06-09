import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import WanderingBot from "./components/WanderingBot";
import ChatPage from "./pages/ChatPage";
import MyBotsPage from "./pages/MyBotsPage";
import PublicBotsPage from "./pages/PublicBotsPage";
import IntegrationsPage from "./pages/IntegrationsPage";
import type { Page, BotState, Session, ChatMessage } from "./types";

export default function App() {
  const [page, setPage] = useState<Page>("Chat");
  const [botState, setBotState] = useState<BotState>("idle");
  const [session, setSession] = useState<Session | null>(null);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem("vaultix-theme");
    if (saved) return saved === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("vaultix-theme", dark ? "dark" : "light");
  }, [dark]);

  function handleSessionStart(s: Session) {
    setSession(s);
    setChatHistory([]);
    setBotState("aside");
    setPage("Chat");
  }

  function handleSessionClear() {
    setSession(null);
    setChatHistory([]);
    setBotState("idle");
  }

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors">
      <Sidebar current={page} onChange={setPage} dark={dark} onToggleDark={() => setDark((d) => !d)} />

      <main className="ml-60 flex-1 min-h-screen overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-8">
          {page === "Chat" && (
            <ChatPage
              session={session}
              chatHistory={chatHistory}
              setChatHistory={setChatHistory}
              setBotState={setBotState}
              onSessionStart={handleSessionStart}
              onSessionClear={handleSessionClear}
            />
          )}
          {page === "My Bots" && (
            <MyBotsPage session={session} onGoToChat={() => setPage("Chat")} />
          )}
          {page === "Public Bots" && (
            <PublicBotsPage onActivate={handleSessionStart} setBotState={setBotState} />
          )}
          {page === "Integrations" && (
            <IntegrationsPage onActivate={handleSessionStart} setBotState={setBotState} />
          )}
        </div>
      </main>

      <WanderingBot state={botState} />
    </div>
  );
}
