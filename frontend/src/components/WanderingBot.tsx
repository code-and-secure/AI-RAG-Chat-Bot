import type { BotState } from "../types";

interface Props {
  state: BotState;
}

export default function WanderingBot({ state }: Props) {
  return (
    <div
      className={`fixed bottom-6 right-6 z-50 pointer-events-none select-none transition-all duration-500 ${
        state === "idle" ? "animate-float-wander" : state === "aside" ? "animate-float-aside" : ""
      }`}
    >
      {/* Wrapper to position the spin ring relative to the avatar */}
      <div className="relative w-16 h-16">
        {/* Spinning ring — only while processing */}
        {state === "processing" && (
          <span className="absolute -inset-1 rounded-full border-4 border-blue-400 border-t-transparent animate-spin" />
        )}

        {/* Avatar image */}
        <div
          className={`w-full h-full rounded-full overflow-hidden shadow-xl transition-all duration-500 ${
            state === "processing"
              ? "ring-2 ring-blue-300/50 shadow-blue-400/60 shadow-2xl scale-110"
              : state === "aside"
              ? "ring-2 ring-blue-500/30 opacity-90 scale-95"
              : "ring-2 ring-blue-600/20"
          }`}
        >
          <img
            src="/robot.png"
            alt="Vaultix Bot"
            className="w-full h-full object-cover"
          />
        </div>
      </div>
    </div>
  );
}
