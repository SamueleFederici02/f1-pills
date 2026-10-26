import React, { useState, useMemo } from 'react';
import { 
  Flame, 
  Search, 
  Calendar, 
  Trophy, 
  Flag, 
  CheckCircle2, 
  Clock, 
  RotateCcw,
  Sparkles,
  Zap
} from 'lucide-react';
import PillCard from './PillCard';

export default function PillsFeed({ 
  pills = [], 
  bookmarks = [], 
  onToggleBookmark, 
  onOpenShare 
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTiming, setSelectedTiming] = useState('all');
  const [minAbsurdity, setMinAbsurdity] = useState(0);

  // Filters focused on temporal race lifecycle:
  const timingFilters = [
    { id: 'all', label: 'Tutto il Weekend di Gara 🏁' },
    { id: 'in_arrivo', label: '🟡 In Arrivo: Pre-Gara Messico' },
    { id: 'appena_passata', label: '🟢 Appena Conclusa: Post-Gara Austin' },
    { id: 'championship_fight', label: '🏆 Lotta Mondiale (Ferrari vs McLaren / Max vs Lando)' },
    { id: 'successiva', label: '🇧🇷 Prossima: Interlagos Sprint' }
  ];

  const filteredPills = useMemo(() => {
    return pills.filter(pill => {
      // Absurdity filter
      if ((pill.absurd || 0.5) < minAbsurdity) return false;

      // Timing / Category filter
      if (selectedTiming !== 'all') {
        if (selectedTiming === 'in_arrivo' && pill.timing_status !== 'in_arrivo') return false;
        if (selectedTiming === 'appena_passata' && pill.timing_status !== 'appena_passata') return false;
        if (selectedTiming === 'championship_fight' && pill.category !== 'championship_fight') return false;
        if (selectedTiming === 'successiva' && pill.timing_status !== 'successiva') return false;
      }

      // Search query filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const titleMatch = pill.title?.toLowerCase().includes(q);
        const subtextMatch = pill.subtext?.toLowerCase().includes(q);
        const driverMatch = pill.driver_name?.toLowerCase().includes(q);
        const keywordsMatch = pill.keywords?.some(k => k.toLowerCase().includes(q));

        if (!titleMatch && !subtextMatch && !driverMatch && !keywordsMatch) {
          return false;
        }
      }

      return true;
    });
  }, [pills, selectedTiming, minAbsurdity, searchQuery]);

  return (
    <div className="space-y-6 pb-20">
      {/* Session-Driven Broadcast Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl glass-panel-elevated border border-white/10 p-5 bg-gradient-to-r from-red-950/50 via-[#10141f] to-amber-950/30">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          {/* Next Race */}
          <div className="p-4 rounded-xl bg-black/40 border border-amber-500/30 space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
              </span>
              <span className="text-[10px] font-mono font-bold uppercase text-amber-400 tracking-wider">
                GARA IN ARRIVO (ROUND 19)
              </span>
            </div>
            <h3 className="font-f1-display font-black text-lg text-white">
              Gran Premio del Messico
            </h3>
            <p className="text-xs text-slate-300 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Domenica 1 Novembre &bull; Autodromo Hermanos Rodriguez (2.240m s.l.m.)</span>
            </p>
          </div>

          {/* Last Race Just Finished */}
          <div className="p-4 rounded-xl bg-black/40 border border-emerald-500/30 space-y-1.5">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[10px] font-mono font-bold uppercase text-emerald-400 tracking-wider">
                GARA APPENA CONCLUSA (ROUND 18)
              </span>
            </div>
            <h3 className="font-f1-display font-black text-lg text-white">
              GP Stati Uniti (Austin) &bull; Doppietta Ferrari
            </h3>
            <p className="text-xs text-slate-300">
              Leclerc 1°, Sainz 2° &bull; Penalità Norris 5s a Curva 12 per il podio
            </p>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="space-y-4">
        {/* Search input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cerca tra le pillole attuali (es. Messico, Austin, Leclerc, Verstappen, Norris, Curva 12, Ferrari)..."
            className="w-full bg-[#121620] border border-white/10 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-red-500 transition-colors shadow-inner"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white text-xs bg-white/10 px-1.5 py-0.5 rounded"
            >
              Reset
            </button>
          )}
        </div>

        {/* Temporal Filters Carousel */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {timingFilters.map((filter) => {
            const isActive = selectedTiming === filter.id;
            return (
              <button
                key={filter.id}
                onClick={() => setSelectedTiming(filter.id)}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border ${
                  isActive
                    ? 'bg-red-600 text-white border-red-500 shadow-lg shadow-red-900/40 scale-105'
                    : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                }`}
              >
                {filter.label}
              </button>
            );
          })}
        </div>

        {/* Absurdity Slider */}
        <div className="glass-panel rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 font-semibold text-slate-300">
              <Flame className="w-4 h-4 text-red-500 fill-red-500" />
              <span>Assurdità minima:</span>
              <span className="font-mono text-red-400 font-bold bg-white/5 px-1.5 py-0.5 rounded">
                {Math.round(minAbsurdity * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="0.90"
              step="0.05"
              value={minAbsurdity}
              onChange={(e) => setMinAbsurdity(parseFloat(e.target.value))}
              className="w-32 sm:w-48 accent-red-600 cursor-pointer"
            />
          </div>

          {(selectedTiming !== 'all' || minAbsurdity > 0 || searchQuery) && (
            <button
              onClick={() => {
                setSelectedTiming('all');
                setMinAbsurdity(0);
                setSearchQuery('');
              }}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-white/5 border border-white/10 text-slate-400 hover:text-white text-xs self-start sm:self-auto"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Azzera Filtri</span>
            </button>
          )}
        </div>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Mostrando <strong>{filteredPills.length}</strong> pillole su questa fase del mondiale</span>
        {minAbsurdity > 0 && <span>Filtro assurdità attivo (&ge; {Math.round(minAbsurdity * 100)}%)</span>}
      </div>

      {/* Pills Grid */}
      {filteredPills.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredPills.map((pill) => (
            <PillCard
              key={pill.id}
              pill={pill}
              isBookmarked={bookmarks.includes(pill.id)}
              onToggleBookmark={onToggleBookmark}
              onOpenShare={onOpenShare}
            />
          ))}
        </div>
      ) : (
        <div className="glass-panel rounded-2xl p-12 text-center space-y-3">
          <Sparkles className="w-10 h-10 text-slate-500 mx-auto" />
          <h4 className="font-f1-display font-bold text-lg text-white">Nessuna pillola trovata</h4>
          <p className="text-slate-400 text-xs max-w-sm mx-auto">
            Seleziona "Tutto il Weekend di Gara" per vedere tutte le pillole pre e post-gara.
          </p>
          <button
            onClick={() => {
              setSelectedTiming('all');
              setMinAbsurdity(0);
              setSearchQuery('');
            }}
            className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-colors"
          >
            Azzera tutti i filtri
          </button>
        </div>
      )}
    </div>
  );
}
