import React, { useState } from 'react';
import { Trophy, Users, Shield, Award, TrendingUp, Flag } from 'lucide-react';
import { TEAM_COLORS } from '../utils/f1Data';

export default function StandingsView({ standings }) {
  const [tab, setTab] = useState('drivers'); // 'drivers' | 'constructors'

  if (!standings) {
    return (
      <div className="glass-panel rounded-2xl p-8 text-center text-slate-400">
        Caricamento classifiche 2026...
      </div>
    );
  }

  const { drivers = [], constructors = [], round = 18, last_race = "GP USA (Austin)" } = standings;

  return (
    <div className="space-y-6 pb-20">
      {/* Header Banner */}
      <div className="glass-panel-elevated rounded-2xl p-6 border border-white/10 bg-gradient-to-r from-red-950/40 via-slate-900 to-indigo-950/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-red-600/30 text-red-300 border border-red-500/30 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider font-f1-display">
                CAMPIONATO MONDIALE FIA 2026
              </span>
              <span className="text-xs text-slate-400 font-mono">DOPO IL ROUND {round} &bull; {last_race.toUpperCase()}</span>
            </div>
            <h2 className="font-f1-display font-black text-2xl text-white">
              Classifica Piloti & Costruttori 2026
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Classifiche ufficiali aggiornate dopo il GP degli Stati Uniti ad Austin. Kimi Antonelli guida il mondiale con 123 punti di margine e ha il Match Point nel prossimo GP del Messico.
            </p>
          </div>

          {/* Toggle Tab */}
          <div className="flex items-center gap-1 bg-black/40 border border-white/10 p-1 rounded-xl self-start sm:self-auto">
            <button
              onClick={() => setTab('drivers')}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-bold transition-all ${
                tab === 'drivers'
                  ? 'bg-red-600 text-white shadow-lg shadow-red-950/50'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Piloti</span>
            </button>

            <button
              onClick={() => setTab('constructors')}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-bold transition-all ${
                tab === 'constructors'
                  ? 'bg-red-600 text-white shadow-lg shadow-red-950/50'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Shield className="w-3.5 h-3.5" />
              <span>Costruttori</span>
            </button>
          </div>
        </div>
      </div>

      {/* CLASSIFICA PILOTI */}
      {tab === 'drivers' && (
        <div className="glass-panel rounded-2xl border border-white/10 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#121620] text-slate-400 font-mono uppercase tracking-wider border-b border-white/10">
                <tr>
                  <th className="py-3 px-4 w-12 text-center">Pos</th>
                  <th className="py-3 px-4">Pilota</th>
                  <th className="py-3 px-4 hidden sm:table-cell">Scuderia</th>
                  <th className="py-3 px-4 text-right">Punti</th>
                  <th className="py-3 px-4 text-right font-mono text-slate-500">Distacco</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-medium">
                {drivers.map((d, index) => {
                  const isLeader = index === 0;
                  const isTop3 = index < 3;
                  const teamInfo = TEAM_COLORS[d.team];

                  return (
                    <tr 
                      key={d.driver_id}
                      className={`hover:bg-white/5 transition-colors ${
                        isLeader ? 'bg-red-950/20' : ''
                      }`}
                    >
                      <td className="py-3 px-4 text-center">
                        <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-f1-display font-black text-xs ${
                          index === 0 ? 'bg-yellow-500 text-black shadow-md shadow-yellow-500/40' :
                          index === 1 ? 'bg-slate-300 text-black' :
                          index === 2 ? 'bg-amber-700 text-white' :
                          'text-slate-400'
                        }`}>
                          {d.position}
                        </span>
                      </td>

                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-f1-display font-bold text-sm text-white">
                            {d.name}
                          </span>
                          {isLeader && (
                            <span className="bg-red-600/30 text-red-300 border border-red-500/40 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">
                              MATCH POINT
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-slate-400 sm:hidden block mt-0.5 capitalize">
                          {d.team?.replace('-', ' ')}
                        </span>
                      </td>

                      <td className="py-3 px-4 hidden sm:table-cell">
                        <span className={`capitalize ${teamInfo?.text || 'text-slate-300'}`}>
                          {teamInfo?.name || d.team?.replace('-', ' ')}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-right font-f1-display font-black text-sm text-white">
                        {d.points}
                      </td>

                      <td className="py-3 px-4 text-right font-mono text-slate-400">
                        {d.gap === 0 ? (
                          <span className="text-yellow-400 font-bold">LEADER</span>
                        ) : (
                          <span>{d.gap}</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CLASSIFICA COSTRUTTORI */}
      {tab === 'constructors' && (
        <div className="glass-panel rounded-2xl border border-white/10 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#121620] text-slate-400 font-mono uppercase tracking-wider border-b border-white/10">
                <tr>
                  <th className="py-3 px-4 w-12 text-center">Pos</th>
                  <th className="py-3 px-4">Costruttore</th>
                  <th className="py-3 px-4 text-right">Punti</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-medium">
                {constructors.map((c, index) => {
                  const isLeader = index === 0;
                  const teamInfo = TEAM_COLORS[c.team_id];

                  return (
                    <tr 
                      key={c.team_id}
                      className={`hover:bg-white/5 transition-colors ${
                        isLeader ? 'bg-red-950/20' : ''
                      }`}
                    >
                      <td className="py-3 px-4 text-center">
                        <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-f1-display font-black text-xs ${
                          index === 0 ? 'bg-yellow-500 text-black shadow-md shadow-yellow-500/40' :
                          index === 1 ? 'bg-slate-300 text-black' :
                          index === 2 ? 'bg-amber-700 text-white' :
                          'text-slate-400'
                        }`}>
                          {c.position}
                        </span>
                      </td>

                      <td className="py-3 px-4">
                        <span className={`font-f1-display font-bold text-sm text-white ${teamInfo?.text || ''}`}>
                          {c.name}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-right font-f1-display font-black text-sm text-white">
                        {c.points}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
