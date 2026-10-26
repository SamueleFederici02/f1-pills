import React, { useState } from 'react';
import { GitBranch, Building2, MapPin, Calendar, ArrowRight, Shield } from 'lucide-react';
import { TEAM_COLORS } from '../utils/f1Data';

export default function LineageView({ lineages = [] }) {
  // Group by lineage_id
  const grouped = lineages.reduce((acc, row) => {
    const id = row.lineage_id;
    if (!acc[id]) acc[id] = [];
    acc[id].push(row);
    return acc;
  }, {});

  const lineageKeys = Object.keys(grouped);
  const [activeKey, setActiveKey] = useState(lineageKeys[0] || 'lineage_mercedes');

  const activeChain = grouped[activeKey] || [];
  const currentTeamInfo = activeChain[activeChain.length - 1];

  const getTeamNameClean = (key) => {
    return key.replace('lineage_', '').replace('_', ' ').toUpperCase();
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Banner */}
      <div className="glass-panel-elevated rounded-2xl p-6 border border-white/10 bg-gradient-to-r from-blue-950/40 via-slate-900 to-teal-950/20">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-teal-600/30 text-teal-300 border border-teal-500/30 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider font-f1-display">
                CONTINUITÀ TECNICA & FABBRICHE
              </span>
              <span className="text-xs text-slate-400 font-mono">LIGNAGGIO SCUDERIE</span>
            </div>
            <h2 className="font-f1-display font-black text-2xl text-white">
              Genealogia Storica dei Team
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Una scuderia non muore con il cambio di sponsor o proprietà: segue la sede e il banco prova. Scopri la discendenza diretta di fabbrica che unisce Tyrrell a Mercedes, Toleman ad Alpine, e Minardi a Faenza.
            </p>
          </div>

          <div className="bg-black/50 border border-white/10 px-4 py-2.5 rounded-xl text-center self-start sm:self-auto">
            <span className="text-[10px] uppercase font-mono text-slate-400">Linee di Fabbrica</span>
            <div className="text-xl font-f1-display font-black text-teal-400">{lineageKeys.length} Scuderie</div>
          </div>
        </div>
      </div>

      {/* Team Lineage Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {lineageKeys.map((key) => {
          const isActive = activeKey === key;
          const chain = grouped[key];
          const latest = chain[chain.length - 1]?.team_name_historical || key;
          return (
            <button
              key={key}
              onClick={() => setActiveKey(key)}
              className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border flex items-center gap-2 ${
                isActive
                  ? 'bg-teal-600 text-white border-teal-500 shadow-lg shadow-teal-950/50 scale-105'
                  : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
              }`}
            >
              <GitBranch className="w-3.5 h-3.5" />
              <span>{latest}</span>
            </button>
          );
        })}
      </div>

      {/* Active Lineage Detailed Card */}
      {currentTeamInfo && (
        <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
            <div>
              <div className="text-xs font-mono text-teal-400 uppercase tracking-wider mb-1">
                LIGNAGGIO: {getTeamNameClean(activeKey)}
              </div>
              <h3 className="font-f1-display font-black text-2xl text-white">
                Da {activeChain[0]?.team_name_historical} a {currentTeamInfo.team_name_historical}
              </h3>
              <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5 text-red-400" />
                <span>Sede storica: <strong>{currentTeamInfo.factory_city}, {currentTeamInfo.factory_country}</strong></span>
              </p>
            </div>

            <div className="bg-white/5 border border-white/10 px-4 py-2 rounded-xl text-right">
              <span className="text-[10px] text-slate-400 font-mono uppercase">Arco Temporale</span>
              <div className="text-sm font-f1-display font-bold text-white">
                {activeChain[0]?.year_from} — {currentTeamInfo.year_to} ({parseInt(currentTeamInfo.year_to) - parseInt(activeChain[0]?.year_from)} anni di storia)
              </div>
            </div>
          </div>

          {/* Interactive Timeline Progression */}
          <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-2.5 sm:before:left-3.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-gradient-to-b before:from-teal-500 before:via-blue-500 before:to-purple-500">
            {activeChain.map((step, idx) => {
              const isLatest = idx === activeChain.length - 1;
              return (
                <div key={idx} className="relative group">
                  {/* Dot */}
                  <div className={`absolute -left-[27px] sm:-left-[35px] top-1.5 w-4 h-4 rounded-full border-2 transition-transform group-hover:scale-125 ${
                    isLatest 
                      ? 'bg-teal-400 border-white shadow-lg shadow-teal-500/50' 
                      : 'bg-[#121620] border-slate-400'
                  }`} />

                  {/* Content card */}
                  <div className={`p-4 rounded-xl border transition-all ${
                    isLatest 
                      ? 'bg-teal-950/20 border-teal-500/30' 
                      : 'bg-white/5 border-white/5 hover:bg-white/10'
                  }`}>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-3">
                        <span className="font-f1-display font-black text-lg text-white">
                          {step.team_name_historical}
                        </span>
                        {isLatest && (
                          <span className="bg-teal-500/20 text-teal-300 border border-teal-500/40 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">
                            Nome Attuale
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2 font-mono text-xs text-slate-300">
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        <span><strong>{step.year_from}</strong> — <strong>{step.year_to}</strong></span>
                      </div>
                    </div>

                    <div className="text-xs text-slate-400 mt-2 flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-slate-500" />
                      <span>Fabbrica a {step.factory_city} ({step.factory_country})</span>
                    </div>
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
