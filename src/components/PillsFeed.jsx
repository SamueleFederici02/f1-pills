import React, { useState, useMemo } from 'react';
import { 
  Flame, 
  Search, 
  Sparkles, 
  Calendar, 
  Trophy, 
  Users, 
  RotateCcw,
  Zap
} from 'lucide-react';
import PillCard from './PillCard';

export default function PillsFeed({ 
  pills = [], 
  bookmarks = [], 
  onToggleBookmark, 
  onOpenShare,
  calendar = []
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDriverGroup, setSelectedDriverGroup] = useState('all');
  const [minAbsurdity, setMinAbsurdity] = useState(0);

  // Driver filters focused strictly on current grid
  const driverFilters = [
    { id: 'all', label: 'Tutti i Piloti di Oggi 🏁' },
    { id: 'top_contenders', label: 'Lotta al Titolo (Max, Charles, Lando) 🏆' },
    { id: 'ferrari', label: 'Scuderia Ferrari 🔴' },
    { id: 'mclaren', label: 'McLaren Papaya 🟠' },
    { id: 'mercedes', label: 'Mercedes-AMG 🟢' },
    { id: 'red_bull', label: 'Red Bull Racing 🔵' },
    { id: 'next_gen', label: 'I Nuovi Fenomeni (Piastri, Antonelli, Bearman) ⚡' },
    { id: 'legends', label: 'Veterani (Alonso, Hamilton, Hülkenberg) 👑' }
  ];

  const filteredPills = useMemo(() => {
    return pills.filter(pill => {
      // Absurdity filter
      if ((pill.absurd || 0.5) < minAbsurdity) return false;

      // Driver Group Filter
      if (selectedDriverGroup !== 'all') {
        const did = pill.driver_id?.toLowerCase() || '';
        const team = pill.team?.toLowerCase() || '';

        if (selectedDriverGroup === 'top_contenders') {
          if (!['max_verstappen', 'charles_leclerc', 'lando_norris'].includes(did)) return false;
        } else if (selectedDriverGroup === 'ferrari') {
          if (!['charles_leclerc', 'lewis_hamilton', 'carlos_sainz'].includes(did) && team !== 'ferrari') return false;
        } else if (selectedDriverGroup === 'mclaren') {
          if (!['lando_norris', 'oscar_piastri'].includes(did) && team !== 'mclaren') return false;
        } else if (selectedDriverGroup === 'mercedes') {
          if (!['george_russell', 'kimi_antonelli', 'lewis_hamilton'].includes(did) && team !== 'mercedes') return false;
        } else if (selectedDriverGroup === 'red_bull') {
          if (!['max_verstappen', 'sergio_perez', 'liam_lawson'].includes(did) && team !== 'red_bull') return false;
        } else if (selectedDriverGroup === 'next_gen') {
          if (!['oscar_piastri', 'kimi_antonelli', 'oliver_bearman', 'franco_colapinto', 'liam_lawson'].includes(did)) return false;
        } else if (selectedDriverGroup === 'legends') {
          if (!['fernando_alonso', 'lewis_hamilton', 'nico_hulkenberg'].includes(did)) return false;
        }
      }

      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const titleMatch = pill.title?.toLowerCase().includes(q);
        const subtextMatch = pill.subtext?.toLowerCase().includes(q);
        const driverMatch = pill.driver_name?.toLowerCase().includes(q) || pill.driver_id?.toLowerCase().includes(q);
        const keywordsMatch = pill.keywords?.some(k => k.toLowerCase().includes(q));

        if (!titleMatch && !subtextMatch && !driverMatch && !keywordsMatch) {
          return false;
        }
      }

      return true;
    });
  }, [pills, selectedDriverGroup, minAbsurdity, searchQuery]);

  return (
    <div className="space-y-6 pb-20">
      {/* Top Banner: Griglia Contemporanea */}
      <div className="relative overflow-hidden rounded-2xl glass-panel-elevated border border-white/10 p-5 bg-gradient-to-r from-red-950/40 via-slate-900/60 to-purple-950/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2 py-0.5 rounded bg-red-600 text-white text-[10px] font-black uppercase tracking-wider font-f1-display">
                PILOTI DI OGGI
              </span>
              <span className="text-xs text-slate-300 font-mono">
                STATISTICHE & COINCIDENZE ATTUALI
              </span>
            </div>
            <h2 className="font-f1-display font-black text-xl sm:text-2xl text-white tracking-tight">
              Pillole della Griglia Contemporanea
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-1">
              Fatti curiosi, record in corso e statistiche dei piloti attualmente in attività, confrontati con la storia della F1.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 backdrop-blur-sm self-start sm:self-auto">
            <Trophy className="w-6 h-6 text-yellow-400 shrink-0" />
            <div>
              <div className="text-[10px] font-mono uppercase text-slate-400">Pillole Attive</div>
              <div className="text-lg font-f1-display font-black text-white">{pills.length} Piloti Attuali</div>
            </div>
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
            placeholder="Cerca per pilota (es. Leclerc, Verstappen, Norris, Hamilton, Antonelli, Piastri)..."
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

        {/* Driver Groups Carousel */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {driverFilters.map((group) => {
            const isActive = selectedDriverGroup === group.id;
            return (
              <button
                key={group.id}
                onClick={() => setSelectedDriverGroup(group.id)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border ${
                  isActive
                    ? 'bg-red-600 text-white border-red-500 shadow-md shadow-red-900/40 scale-105'
                    : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10 hover:border-white/20'
                }`}
              >
                {group.label}
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

          {(selectedDriverGroup !== 'all' || minAbsurdity > 0 || searchQuery) && (
            <button
              onClick={() => {
                setSelectedDriverGroup('all');
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
        <span>Mostrando <strong>{filteredPills.length}</strong> pillole su piloti contemporanei</span>
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
            Prova ad abbassare lo slider dell'assurdità o a selezionare "Tutti i Piloti di Oggi".
          </p>
          <button
            onClick={() => {
              setSelectedDriverGroup('all');
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
