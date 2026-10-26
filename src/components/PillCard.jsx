import React, { useState } from 'react';
import { 
  Bookmark, 
  Share2, 
  Flame, 
  ChevronDown, 
  ChevronUp, 
  Check, 
  Trophy, 
  Calendar, 
  Compass, 
  Sparkles,
  Zap
} from 'lucide-react';
import { TEAM_COLORS, CATEGORY_LABELS } from '../utils/f1Data';

export default function PillCard({ 
  pill, 
  isBookmarked, 
  onToggleBookmark, 
  onOpenShare 
}) {
  const [expanded, setExpanded] = useState(false);
  const [showDelirio, setShowDelirio] = useState(false);
  const [copied, setCopied] = useState(false);

  // Extract metadata and styling
  const isDebunked = pill.state === 'tabu_sfatato' || pill.pattern === 'tabu_sfatato';
  const isDelirio = pill.state === 'delirio' || (pill.absurd && pill.absurd >= 0.85);
  const absurdityPct = Math.round((pill.absurd || 0.5) * 100);

  // Accent colors based on team and state
  const teamInfo = TEAM_COLORS[pill.team];
  let accentBorder = teamInfo ? teamInfo.border : 'border-white/10';
  let accentBg = 'bg-white/5';
  let accentBadge = 'bg-white/10 text-slate-300 border-white/20';

  if (pill.team === 'ferrari') {
    accentBorder = 'border-red-600/40 shadow-red-950/20 shadow-lg';
    accentBg = 'bg-red-950/15';
    accentBadge = 'bg-red-600/20 text-red-300 border-red-500/40';
  } else if (pill.team === 'mclaren') {
    accentBorder = 'border-orange-500/40 shadow-orange-950/20 shadow-lg';
    accentBg = 'bg-orange-950/15';
    accentBadge = 'bg-orange-500/20 text-orange-300 border-orange-500/40';
  } else if (pill.team === 'red_bull') {
    accentBorder = 'border-blue-600/40 shadow-blue-950/20 shadow-lg';
    accentBg = 'bg-blue-950/15';
    accentBadge = 'bg-blue-600/20 text-blue-300 border-blue-500/40';
  } else if (pill.team === 'mercedes') {
    accentBorder = 'border-teal-500/40 shadow-teal-950/20 shadow-lg';
    accentBg = 'bg-teal-950/15';
    accentBadge = 'bg-teal-500/20 text-teal-300 border-teal-500/40';
  } else if (pill.team === 'aston_martin') {
    accentBorder = 'border-emerald-600/40';
    accentBg = 'bg-emerald-950/15';
    accentBadge = 'bg-emerald-600/20 text-emerald-300 border-emerald-500/40';
  } else if (pill.badge?.includes('RECORD')) {
    accentBorder = 'border-purple-500/40 shadow-purple-950/20 shadow-lg';
    accentBg = 'bg-purple-950/20';
    accentBadge = 'bg-purple-500/20 text-purple-300 border-purple-500/40';
  }

  const categoryInfo = CATEGORY_LABELS[pill.category] || {
    label: 'Statistica Storica',
    color: 'bg-blue-500/20 text-blue-300 border-blue-500/30'
  };

  const handleQuickCopy = (e) => {
    e.stopPropagation();
    const textToCopy = `🏁 F1 PILLS: ${pill.title}\n${pill.subtext}\n\n👉 f1pills.web.app`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <article className={`glass-panel rounded-2xl border transition-all duration-300 hover:border-white/25 overflow-hidden flex flex-col justify-between ${accentBorder} ${accentBg}`}>
      {/* Top Card Header */}
      <div className="p-5 pb-3">
        <div className="flex items-start justify-between gap-3 mb-2.5">
          <div className="flex flex-wrap items-center gap-1.5">
            {pill.driver_name && (
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black uppercase tracking-wider bg-white/10 text-white border border-white/20 font-f1-display">
                🏎️ {pill.driver_name}
              </span>
            )}
            {pill.badge && (
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider border font-f1-display ${accentBadge}`}>
                {pill.badge}
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {/* Absurdity indicator */}
            <div 
              className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-mono border ${
                absurdityPct >= 80 
                  ? 'bg-red-500/20 text-red-300 border-red-500/40' 
                  : 'bg-white/5 text-slate-400 border-white/10'
              }`}
              title={`Indice di Assurdità: ${absurdityPct}%`}
            >
              <Flame className={`w-3 h-3 ${absurdityPct >= 80 ? 'text-red-400 fill-red-400' : 'text-slate-400'}`} />
              <span>{absurdityPct}%</span>
            </div>

            <button
              onClick={() => onToggleBookmark(pill.id)}
              className={`p-1.5 rounded-lg border transition-colors ${
                isBookmarked 
                  ? 'bg-red-600/30 border-red-500 text-red-400' 
                  : 'bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10'
              }`}
              title={isBookmarked ? "Rimuovi dai salvati" : "Salva pillola"}
            >
              <Bookmark className={`w-3.5 h-3.5 ${isBookmarked ? 'fill-red-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Level 1: Main Punchy Broadcast Title */}
        <h3 className="font-f1-display font-bold text-lg sm:text-xl text-white leading-snug tracking-tight mb-2">
          {pill.title}
        </h3>

        {/* Main Subtext */}
        <p className="text-slate-300 text-sm leading-relaxed font-normal">
          {pill.subtext}
        </p>
      </div>

      {/* Level 2: Expanded Conditions */}
      {expanded && (
        <div className="px-5 py-3 border-t border-white/10 bg-black/40 text-xs text-slate-300 space-y-2.5 animate-fadeIn">
          <div className="flex items-center justify-between pb-1.5 border-b border-white/5 font-semibold text-slate-400 uppercase tracking-wider text-[10px]">
            <span>Dettagli Tecnici & Condizioni</span>
            <span>Pattern: {pill.pattern || 'storico'}</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-slate-300">
            {pill.year && (
              <div className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>Anno: <strong>{pill.year}</strong></span>
              </div>
            )}
            {pill.circuit_id && (
              <div className="flex items-center gap-1.5">
                <Compass className="w-3.5 h-3.5 text-slate-400" />
                <span>Circuito: <strong>{pill.circuit_id}</strong></span>
              </div>
            )}
            {pill.subject && (
              <div className="col-span-2 flex items-center gap-1.5">
                <Trophy className="w-3.5 h-3.5 text-amber-400" />
                <span>Soggetto: <code className="bg-white/10 px-1 py-0.5 rounded text-[11px]">{pill.subject}</code></span>
              </div>
            )}
          </div>

          {pill.keywords && pill.keywords.length > 0 && (
            <div className="pt-1 flex flex-wrap gap-1">
              {pill.keywords.slice(0, 6).map((k, i) => (
                <span key={i} className="bg-white/5 border border-white/10 text-slate-400 px-1.5 py-0.5 rounded text-[10px]">
                  #{k}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Level 3: Modalità Delirio Deep Trivia */}
      {showDelirio && (
        <div className="px-5 py-3 border-t border-red-500/20 bg-red-950/30 text-xs text-red-200 space-y-1.5">
          <div className="flex items-center gap-1.5 font-bold text-red-400 text-[11px] uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Modalità Delirio: Livello 3 Deep Trivia</span>
          </div>
          <p className="text-slate-200 text-xs leading-relaxed">
            {pill.delirio_text || `Coincidenza estrema calcolata su oltre 1.100 Gran Premi. Inclusi predicati su ordinamenti legislativi, geopolitica, cibi, fuso orario e biometria dal database DuckDB relazionale.`}
          </p>
        </div>
      )}

      {/* Card Footer Bar */}
      <div className="p-4 pt-2.5 flex items-center justify-between border-t border-white/5 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          {/* Level 2 expand toggle */}
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-slate-400 hover:text-white transition-colors text-[11px] font-medium"
          >
            {expanded ? (
              <>
                <span>Meno dettagli</span>
                <ChevronUp className="w-3.5 h-3.5" />
              </>
            ) : (
              <>
                <span>Dettagli tecnici</span>
                <ChevronDown className="w-3.5 h-3.5" />
              </>
            )}
          </button>

          {/* Level 3 Delirio Toggle */}
          <button
            onClick={() => setShowDelirio(!showDelirio)}
            className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold border transition-all ${
              showDelirio 
                ? 'bg-red-600 text-white border-red-500' 
                : 'bg-white/5 text-slate-300 border-white/10 hover:bg-red-950/40 hover:text-red-300'
            }`}
            title="Mostra curiosità estreme e predicati assurdi"
          >
            <Zap className="w-3 h-3 text-yellow-400" />
            <span>Delirio</span>
          </button>
        </div>

        {/* Share buttons */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleQuickCopy}
            className="p-1.5 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-slate-300 hover:text-white transition-colors"
            title="Copia testo per WhatsApp / Telegram"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <span className="text-[10px] font-semibold">Copia</span>}
          </button>

          <button
            onClick={() => onOpenShare(pill)}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-red-600 hover:bg-red-700 text-white text-[11px] font-bold shadow-md shadow-red-900/30 transition-all hover:scale-105"
            title="Condividi come card su Instagram Stories o WhatsApp"
          >
            <Share2 className="w-3 h-3" />
            <span>Condividi</span>
          </button>
        </div>
      </div>
    </article>
  );
}
