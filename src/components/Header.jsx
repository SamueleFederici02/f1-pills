import React from 'react';
import { Flag, Sparkles, Sliders, Bookmark, HelpCircle } from 'lucide-react';

export default function Header({ 
  currentTab, 
  setCurrentTab, 
  savedCount, 
  openSettings, 
  pillsCount,
  anomaliesCount
}) {
  return (
    <header className="sticky top-0 z-30 glass-panel border-b border-white/10 backdrop-blur-md">
      {/* Broadcast Ticker Bar */}
      <div className="bg-[#121620] border-b border-white/5 px-4 py-1.5 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-emerald-400 font-bold uppercase tracking-wider text-[11px]">F1 TV TIMING SYSTEM</span>
          <span className="text-white/30">|</span>
          <span className="text-slate-400 hidden sm:inline">DATABASE STORICO 1950–2026</span>
        </div>
        <div className="flex items-center gap-3 text-slate-300">
          <span className="bg-red-600/30 text-red-400 border border-red-500/30 px-2 py-0.5 rounded text-[10px] font-bold">
            {pillsCount} PILLS
          </span>
          <span className="bg-purple-600/30 text-purple-400 border border-purple-500/30 px-2 py-0.5 rounded text-[10px] font-bold hidden sm:inline">
            {anomaliesCount} ANOMALIE
          </span>
        </div>
      </div>

      {/* Main App Navigation Header */}
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div 
          onClick={() => setCurrentTab('feed')} 
          className="flex items-center gap-2.5 cursor-pointer group"
        >
          <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-red-600 to-red-800 flex items-center justify-center shadow-lg shadow-red-900/40 border border-red-500/50 group-hover:scale-105 transition-transform">
            <Flag className="w-5 h-5 text-white transform -rotate-12" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-f1-display font-black text-xl tracking-tight text-white">
                F1 <span className="text-red-500">PILLS</span>
              </span>
              <span className="text-[10px] bg-white/10 text-slate-300 px-1.5 py-0.5 rounded font-mono uppercase tracking-wide">
                PWA
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium">Curiosità, Coincidenze & Record</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentTab('bookmarks')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              currentTab === 'bookmarks'
                ? 'bg-red-600/30 border-red-500 text-red-300'
                : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Salvati</span>
            {savedCount > 0 && (
              <span className="bg-red-600 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">
                {savedCount}
              </span>
            )}
          </button>

          <button
            onClick={openSettings}
            className="p-2 rounded-lg bg-white/5 border border-white/10 text-slate-300 hover:bg-white/10 transition-colors"
            title="Impostazioni & Installazione PWA"
          >
            <Sliders className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
