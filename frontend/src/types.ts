export type Page = "Chat" | "My Bots" | "Public Bots" | "Integrations";
export type BotState = "idle" | "processing" | "aside";
export type PublicBotType = "finance" | "hr" | "legal";

export interface ChatMessage {
  question: string;
  answer: string;
  usedWeb: boolean;
}

export interface Session {
  id: string;
  name: string;
  chunks: number;
}

export interface Stats {
  total_queries: number;
  total_docs: number;
  total_bots: number;
}
