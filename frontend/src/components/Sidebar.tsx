import type { Page } from "../types";

const NAV_ITEMS: { label: Page; icon: string }[] = [
  { label: "Chat", icon: "💬" },
  { label: "My Bots", icon: "📁" },
  { label: "Public Bots", icon: "🤖" },
  { label: "Integrations", icon: "🔌" },
];

interface Props {
  current: Page;
  onChange: (p: Page) => void;
  dark: boolean;
  onToggleDark: () => void;
}

export default function Sidebar({ current, onChange, dark, onToggleDark }: Props) {
  return (
    <aside className="fixed inset-y-0 left-0 w-60 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col z-40 transition-colors">
      {/* Logo */}
      <div className="px-5 pt-6 pb-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center text-lg">🔷</div>
          <div>
            <div className="font-bold text-gray-900 dark:text-white leading-tight tracking-wide">Vaultix</div>
            <div className="text-gray-400 text-xs">THINK. EXECUTE. REPEAT.</div>
          </div>
        </div>
      </div>

      {/* Search placeholder */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-xl px-3 py-2 text-gray-400 text-sm">
          <span>🔍</span>
          <span>Search in chats</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ label, icon }) => (
          <button
            key={label}
            onClick={() => onChange(label)}
            className={`nav-btn ${current === label ? "nav-btn-active" : "nav-btn-inactive"}`}
          >
            <span>{icon}</span>
            <span>{label}</span>
          </button>
        ))}
      </nav>

      {/* Footer: theme toggle + version */}
      <div className="px-4 py-4 border-t border-gray-200 dark:border-gray-800 space-y-3">
        <button
          onClick={onToggleDark}
          className="flex items-center justify-between w-full px-3 py-2 rounded-xl bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          <span>{dark ? "🌙 Dark Mode" : "☀️ Light Mode"}</span>
          <span className={`w-9 h-5 rounded-full transition-colors relative ${dark ? "bg-blue-600" : "bg-gray-300"}`}>
            <span className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all ${dark ? "left-4" : "left-0.5"}`} />
          </span>
        </button>
        <p className="text-xs text-gray-400 dark:text-gray-600 px-1">Vaultix v1.0.0</p>
      </div>
    </aside>
  );
}
