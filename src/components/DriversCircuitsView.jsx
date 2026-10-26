import React, { useState, useMemo } from 'react';
import { 
  Users, 
  Compass, 
  Search, 
  MapPin, 
  Calendar, 
  Sparkles, 
  Check, 
  X,
  Flame,
  Globe2,
  TrendingUp,
  Award
} from 'lucide-react';
import { ZODIAC_EMOJIS, ELEMENT_COLORS } from '../utils/f1Data';

export default function DriversCircuitsView({ 
  drivers = [], 
  circuits = [] 
}) {
  const [subTab, setSubTab] = useState('drivers'); // 'drivers' | 'circuits'
  const [search, setSearch] = useState('');
  const [filterLeftHanded, setFilterLeftHanded] = useState(false);
  const [filterPredicate, setFilterPredicate] = useState('all');

  // Filtered drivers (drivers with wikipedia_url or modern or known height/code)
  const filteredDrivers = useMemo(() => {
    return drivers.filter(d => {
      if (filterLeftHanded && d.is_left_handed !== '1') return false;

      if (search.trim()) {
        const q = search.toLowerCase().trim();
        const matchName = d.name?.toLowerCase().includes(q);
        const matchNat = d.nationality?.toLowerCase().includes(q);
        const matchSign = d.zodiac_sign?.toLowerCase().includes(q);
        const matchElem = d.zodiac_element?.toLowerCase().includes(q);
        if (!matchName && !matchNat && !matchSign && !matchElem) return false;
      }
      return true;
    }).slice(0, 80); // top 80 for fast rendering
  }, [drivers, search, filterLeftHanded]);

  // Filtered circuits
  const filteredCircuits = useMemo(() => {
    return circuits.filter(c => {
      if (filterPredicate !== 'all') {
        if (c[filterPredicate] !== '1') return false;
      }

      if (search.trim()) {
        const q = search.toLowerCase().trim();
        const matchName = c.circuit_name?.toLowerCase().includes(q);
        const matchLoc = c.locality?.toLowerCase().includes(q);
        const matchCountry = c.country?.toLowerCase().includes(q);
        if (!matchName && !matchLoc && !matchCountry) return false;
      }
      return true;
    });
  }, [circuits, search, filterPredicate]);

  return (
    <div className="space-y-6 pb-20">
      {/* Sub Tabs Toggle */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-1 bg-white/5 p-1 rounded-xl border border-white/10">
          <button
            onClick={() => setSubTab('drivers')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              subTab === 'drivers'
                ? 'bg-red-600 text-white shadow-md shadow-red-900/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Piloti & Biometria ({drivers.length})</span>
          </button>

          <button
            onClick={() => setSubTab('circuits')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              subTab === 'circuits'
                ? 'bg-red-600 text-white shadow-md shadow-red-900/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Circuiti & Predicati ({circuits.length})</span>
          </button>
        </div>
      </div>

      {/* DRIVERS SUBTAB */}
      {subTab === 'drivers' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Cerca pilota per nome, nazionalità o segno zodiacale..."
                className="w-full bg-[#121620] border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-red-500"
              />
            </div>

            <button
              onClick={() => setFilterLeftHanded(!filterLeftHanded)}
              className={`flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl border text-xs font-semibold whitespace-nowrap transition-all ${
                filterLeftHanded
                  ? 'bg-amber-600/30 border-amber-500 text-amber-300'
                  : 'bg-white/5 border-white/10 text-slate-400 hover:text-white'
              }`}
            >
              <span>Solo Mancini (Senna, Alonso, Button...)</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {filteredDrivers.map((d) => {
              const isMancino = d.is_left_handed === '1';
              const elemColor = ELEMENT_COLORS[d.zodiac_element] || 'text-slate-400 border-white/10 bg-white/5';
              const emoji = ZODIAC_EMOJIS[d.zodiac_sign] || '⭐';

              return (
                <div 
                  key={d.driver_id}
                  className={`glass-panel rounded-xl p-4 border transition-all ${
                    isMancino ? 'border-amber-500/40 bg-amber-950/10' : 'border-white/5 hover:border-white/20'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <div>
                      <h4 className="font-f1-display font-bold text-base text-white">
                        {d.name}
                      </h4>
                      <p className="text-[11px] text-slate-400">{d.nationality}</p>
                    </div>

                    {isMancino && (
                      <span className="bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">
                        MANCINO 🥊
                      </span>
                    )}
                  </div>

                  <div className="pt-2 border-t border-white/5 grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block">Statura</span>
                      <span className="font-medium text-slate-300">
                        {d.height_cm ? `${d.height_cm} cm` : 'Dato storico n.d.'}
                      </span>
                    </div>

                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block">Oroscopo F1</span>
                      {d.zodiac_sign ? (
                        <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium border ${elemColor}`}>
                          <span>{emoji} {d.zodiac_sign}</span>
                        </span>
                      ) : (
                        <span className="text-slate-500">—</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* CIRCUITS SUBTAB */}
      {subTab === 'circuits' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Cerca circuito per nome o nazione (es. Monza, Spa, Monaco, Las Vegas)..."
                className="w-full bg-[#121620] border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-red-500"
              />
            </div>

            {/* Predicate Quick Filter Dropdown */}
            <select
              value={filterPredicate}
              onChange={(e) => setFilterPredicate(e.target.value)}
              className="bg-[#121620] border border-white/10 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none focus:border-red-500"
            >
              <option value="all">Tutti i Predicati</option>
              <option value="counter_clockwise">Antiorario (Interlagos, Baku, Yas Marina...)</option>
              <option value="night_race">Notturna (Singapore, Bahrain, Las Vegas...)</option>
              <option value="high_altitude">Alta Quota (&gt; 600m s.l.m.)</option>
              <option value="street_circuit">Cittadino (Monaco, Melbourne, Baku...)</option>
              <option value="zero_income_tax">Zero Imposte sul Reddito</option>
              <option value="equal_marriage_legal">Matrimonio Egualitario</option>
              <option value="alcohol_podium_banned">Divieto Alcol sul Podio</option>
              <option value="e171_food_legal">Biossido Titanio E171 Legale</option>
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {filteredCircuits.map((c) => {
              return (
                <div 
                  key={c.circuit_id}
                  className="glass-panel rounded-xl p-4 border border-white/5 hover:border-white/20 transition-all space-y-2.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-f1-display font-bold text-base text-white leading-snug">
                        {c.circuit_name}
                      </h4>
                      <p className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                        <MapPin className="w-3 h-3 text-red-400" />
                        <span>{c.locality}, {c.country}</span>
                      </p>
                    </div>

                    <span className="font-mono text-[10px] bg-white/5 border border-white/10 px-2 py-0.5 rounded text-slate-300 shrink-0">
                      {c.total_races} GP
                    </span>
                  </div>

                  {/* Badges of physical and normative predicates */}
                  <div className="flex flex-wrap gap-1 pt-1 border-t border-white/5">
                    {c.counter_clockwise === '1' && (
                      <span className="bg-red-500/20 text-red-300 border border-red-500/40 text-[10px] px-1.5 py-0.5 rounded">
                        ↺ Antiorario
                      </span>
                    )}
                    {c.night_race === '1' && (
                      <span className="bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] px-1.5 py-0.5 rounded">
                        🌙 Notturna
                      </span>
                    )}
                    {c.high_altitude === '1' && (
                      <span className="bg-purple-500/20 text-purple-300 border border-purple-500/40 text-[10px] px-1.5 py-0.5 rounded">
                        ⛰️ Quota &gt;600m
                      </span>
                    )}
                    {c.street_circuit === '1' && (
                      <span className="bg-blue-500/20 text-blue-300 border border-blue-500/40 text-[10px] px-1.5 py-0.5 rounded">
                        🏙️ Cittadino
                      </span>
                    )}
                    {c.zero_income_tax === '1' && (
                      <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] px-1.5 py-0.5 rounded">
                        💰 Tasse 0%
                      </span>
                    )}
                    {c.chewing_gum_banned === '1' && (
                      <span className="bg-pink-500/20 text-pink-300 border border-pink-500/40 text-[10px] px-1.5 py-0.5 rounded">
                        🚫 No Chewing Gum
                      </span>
                    )}
                    {c.kinder_surprise_banned === '1' && (
                      <span className="bg-yellow-500/20 text-yellow-300 border border-yellow-500/40 text-[10px] px-1.5 py-0.5 rounded">
                        🚫 No Kinder Sorpresa
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
