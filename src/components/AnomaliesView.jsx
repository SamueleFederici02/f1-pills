import React, { useState, useMemo } from 'react';
import { 
  Trophy, 
  Calendar, 
  Compass, 
  Search, 
  Filter, 
  Bookmark, 
  Share2, 
  Flame, 
  Sparkles,
  Car
} from 'lucide-react';
import { CATEGORY_LABELS, TEAM_COLORS } from '../utils/f1Data';

export default function AnomaliesView({ 
  anomalies = [],
  onOpenShare
}) {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    { id: 'all', label: 'Tutte le 107 Storie' },
    { id: 'finish_anomalies', label: 'Arrivi Bizzarri (11)' },
    { id: 'historic_milestones', label: 'Pietre Miliari (32)' },
    { id: 'heroic_drives', label: 'Imprese Eroiche (22)' },
    { id: 'bizarre_moments', label: 'Episodi Bizzarri (20)' },
    { id: 'chaos_races', label: 'Gare nel Caos (9)' },
    { id: 'scandals', label: 'Scandali & Veleni (13)' }
  ];

  const filtered = useMemo(() => {
    return anomalies.filter(item => {
      if (selectedCategory !== 'all' && item.category !== selectedCategory) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const matchTitle = item.title?.toLowerCase().includes(q);
        const matchDesc = item.description?.toLowerCase().includes(q);
        const matchGp = item.grand_prix?.toLowerCase().includes(q);
        const matchDriver = item.driver_id?.toLowerCase().includes(q);
        const matchKeys = item.keywords?.toLowerCase().includes(q);
        const matchYear = String(item.year).includes(q);

        if (!matchTitle && !matchDesc && !matchGp && !matchDriver && !matchKeys && !matchYear) {
          return false;
        }
      }
      return true;
    });
  }, [anomalies, selectedCategory, searchQuery]);

  return (
    <div className="space-y-6 pb-20">
      {/* Header Banner */}
      <div className="glass-panel-elevated rounded-2xl p-6 border border-white/10 bg-gradient-to-r from-purple-950/40 via-slate-900 to-amber-950/20">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-purple-600/30 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider font-f1-display">
                ARCHIVIO ANOMALIE STORICHE
              </span>
              <span className="text-xs text-slate-400 font-mono">1950–2026 CENSIMENTO UFFICIALE</span>
            </div>
            <h2 className="font-f1-display font-black text-2xl text-white">
              Le 107 Grandi Anomalie della F1
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Dettagli leggendari che i normali registri FIA non raccontano: arrivi su tre ruote, vittorie ai box, piloti che spingono a braccia svenuti sul traguardo, scandali e carambole meteorologiche.
            </p>
          </div>

          <div className="bg-black/50 border border-white/10 px-4 py-2.5 rounded-xl text-center self-start sm:self-auto">
            <span className="text-[10px] uppercase font-mono text-slate-400">Episodi Registrati</span>
            <div className="text-xl font-f1-display font-black text-purple-400">{anomalies.length} Record</div>
          </div>
        </div>
      </div>

      {/* Filter and Search */}
      <div className="space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cerca un'anomalia (es. 3 ruote, compleanno, pit lane, Dallas, tombino, Pescara, kilt)..."
            className="w-full bg-[#121620] border border-white/10 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition-colors shadow-inner"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {categories.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedCategory(c.id)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border ${
                selectedCategory === c.id
                  ? 'bg-purple-600 text-white border-purple-500 shadow-md shadow-purple-900/40 scale-105'
                  : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {/* Results Count */}
      <div className="text-xs text-slate-400 px-1">
        Mostrando <strong>{filtered.length}</strong> storie storiche
      </div>

      {/* Anomalies List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((item) => {
          const categoryInfo = CATEGORY_LABELS[item.category] || {
            label: item.category,
            color: 'bg-white/10 text-slate-300 border-white/20'
          };

          return (
            <div 
              key={item.id}
              className="glass-panel rounded-2xl p-5 border border-white/10 hover:border-purple-500/40 transition-all flex flex-col justify-between space-y-3 group"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="font-mono text-[11px] font-bold text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
                      #{item.id}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${categoryInfo.color}`}>
                      {categoryInfo.label}
                    </span>
                  </div>

                  <span className="font-f1-display font-bold text-sm text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                    {item.year}
                  </span>
                </div>

                <h3 className="font-f1-display font-bold text-lg text-white group-hover:text-purple-300 transition-colors leading-snug">
                  {item.title}
                </h3>

                <p className="text-slate-300 text-xs sm:text-sm mt-2 leading-relaxed">
                  {item.description}
                </p>
              </div>

              <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-slate-300">
                    GP: <strong>{item.grand_prix}</strong>
                  </span>
                  {item.driver_id && (
                    <>
                      <span className="text-white/20">•</span>
                      <span className="capitalize">{item.driver_id.replace('_', ' ')}</span>
                    </>
                  )}
                </div>

                <button
                  onClick={() => onOpenShare({
                    title: `${item.title} (${item.year})`,
                    subtext: item.description,
                    badge: `ANOMALIA #${item.id}`,
                    category: item.category
                  })}
                  className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white transition-colors"
                  title="Condividi storia"
                >
                  <Share2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
