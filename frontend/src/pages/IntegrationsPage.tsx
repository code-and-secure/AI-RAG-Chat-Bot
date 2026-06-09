import { useState } from "react";
import { scrapeUrl } from "../api";
import type { BotState, Session } from "../types";

interface Props {
  onActivate: (s: Session) => void;
  setBotState: (s: BotState) => void;
}

export default function IntegrationsPage({ onActivate, setBotState }: Props) {
  const [crawlUrl, setCrawlUrl] = useState("");
  const [crawling, setCrawling] = useState(false);
  const [crawlError, setCrawlError] = useState("");
  const [slackToken, setSlackToken] = useState("");
  const [slackMsg, setSlackMsg] = useState("");

  async function handleCrawl(e: React.FormEvent) {
    e.preventDefault();
    if (!crawlUrl.trim()) return;
    setCrawlError("");
    setCrawling(true);
    setBotState("processing");
    try {
      const res = await scrapeUrl(crawlUrl.trim());
      onActivate({ id: res.session_id, name: res.name, chunks: res.chunks });
    } catch (err: unknown) {
      setCrawlError(err instanceof Error ? err.message : "Scrape failed");
      setBotState("idle");
    } finally {
      setCrawling(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">
          Connect Your <span className="text-blue-600 dark:text-blue-400">Workspace</span>
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">
          Connect Vaultix to your tools to ingest documents or interact via chat channels.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Web Scraper */}
        <div className="card space-y-4">
          <div className="text-3xl">🕸️</div>
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white text-lg">Website Scraper &amp; Crawler</h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
              Enter any website URL to scrape its text, train the RAG vector DB, and chat about it instantly.
            </p>
          </div>
          <form onSubmit={handleCrawl} className="space-y-3">
            <input className="input" placeholder="https://example.com" value={crawlUrl} onChange={(e) => setCrawlUrl(e.target.value)} disabled={crawling} />
            {crawlError && <p className="text-red-500 text-xs">{crawlError}</p>}
            <button type="submit" className="btn-primary w-full" disabled={crawling || !crawlUrl.trim()}>
              {crawling ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Scraping &amp; building database…
                </span>
              ) : (
                "Crawl & Train"
              )}
            </button>
          </form>
        </div>

        {/* Slack */}
        <div className="card space-y-4">
          <div className="text-3xl">💬</div>
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white text-lg">Slack Integration</h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
              Deploy your RAG bot as a Slack app. Let your team query documents via channels or DMs.
            </p>
          </div>
          <input className="input" placeholder="xoxb-xxxx-xxxx" type="password" value={slackToken} onChange={(e) => setSlackToken(e.target.value)} />
          {slackMsg && <p className="text-emerald-600 dark:text-emerald-400 text-sm">{slackMsg}</p>}
          <button className="btn-primary w-full" onClick={() => { if (slackToken) setSlackMsg("✅ Slack Bot verified and connected! (Mock)"); }}>
            Enable Slack Bot
          </button>
        </div>

        {/* Google Drive */}
        <div className="card space-y-4">
          <div className="text-3xl">🤖</div>
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white text-lg">Google Drive Sync</h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
              Automatically fetch, index, and sync documents from your Google Drive folders.
            </p>
          </div>
          <button className="btn-secondary w-full" onClick={() => alert("Google OAuth login would trigger here. (Future Roadmap)")}>
            Connect Google Drive
          </button>
        </div>

        {/* Notion */}
        <div className="card space-y-4">
          <div className="text-3xl">📓</div>
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white text-lg">Notion Integration</h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
              Connect Notion API to index workspace pages and query documentation databases from chat.
            </p>
          </div>
          <button className="btn-secondary w-full" onClick={() => alert("Notion Integrations portal would open here. (Future Roadmap)")}>
            Connect Notion
          </button>
        </div>
      </div>
    </div>
  );
}
