import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import PillsFeed from './components/PillsFeed';
import SearchWhatIf from './components/SearchWhatIf';
import AnomaliesView from './components/AnomaliesView';
import LineageView from './components/LineageView';
import DriversCircuitsView from './components/DriversCircuitsView';
import SettingsModal from './components/SettingsModal';
import SocialShareModal from './components/SocialShareModal';
import PillCard from './components/PillCard';

import { 
  Flame, 
  HelpCircle, 
  GitBranch, 
  Users, 
  Sparkles, 
  Bookmark, 
  Compass, 
  Layers
} from 'lucide-react';

export default function App() {
  const [currentTab, setCurrentTab] = useState('feed'); // 'feed' | 'anomalies' | 'whatif' | 'lineages' | 'db' | 'bookmarks'
  const [pills, setPills] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [circuits, setCircuits] = useState([]);
  const [lineages, setLineages] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [calendar, setCalendar] = useState([]);
  const [loading, setLoading] = useState(true);

  // Bookmarks in localStorage
  const [bookmarks, setBookmarks] = useState(() => {
    try {
      const saved = localStorage.getItem('f1_pills_bookmarks');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // BYOK Gemini key
  const [apiKey, setApiKey] = useState(() => {
    return localStorage.getItem('f1_pills_gemini_key') || '';
  });

  // Modals state
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [sharePill, setSharePill] = useState(null);

  // Fetch all data
  useEffect(() => {
    async function loadAllData() {
      try {
        const [
          pillsRes,
          anomaliesRes,
          circuitsRes,
          lineagesRes,
          driversRes,
          calendarRes
        ] = await Promise.all([
          fetch('/data/pills.json'),
          fetch('/data/anomalies.json'),
          fetch('/data/circuits.json'),
          fetch('/data/lineages.json'),
          fetch('/data/drivers.json'),
          fetch('/data/calendar.json')
        ]);

        const [
          pillsData,
          anomaliesData,
          circuitsData,
          lineagesData,
          driversData,
          calendarData
        ] = await Promise.all([
          pillsRes.json(),
          anomaliesRes.json(),
          circuitsRes.json(),
          lineagesRes.json(),
          driversRes.json(),
          calendarRes.json()
        ]);

        setPills(pillsData);
        setAnomalies(anomaliesData);
        setCircuits(circuitsData);
        setLineages(lineagesData);
        setDrivers(driversData);
        setCalendar(calendarData);
      } catch (err) {
        console.error("Errore nel caricamento dei dati:", err);
      } finally {
        setLoading(false);
      }
    }

    loadAllData();
  }, []);

  // Toggle bookmark
  const toggleBookmark = (id) => {
    setBookmarks(prev => {
      let updated;
      if (prev.includes(id)) {
        updated = prev.filter(x => x !== id);
      } else {
        updated = [...prev, id];
      }
      localStorage.setItem('f1_pills_bookmarks', JSON.stringify(updated));
      return updated;
    });
  };

  const bookmarkedPills = pills.filter(p => bookmarks.includes(p.id));

  return (
    <div className="min-h-screen bg-carbon flex flex-col text-slate-100">
      {/* Top Header */}
      <Header
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        savedCount={bookmarks.length}
        openSettings={() => setSettingsOpen(true)}
        pillsCount={pills.length}
        anomaliesCount={anomalies.length}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
            <div className="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
            <p className="font-f1-display font-bold text-slate-400 text-sm tracking-wide">
              CARICAMENTO DATABASE F1...
            </p>
          </div>
        ) : (
          <>
            {/* Tab: Feed */}
            {currentTab === 'feed' && (
              <PillsFeed
                pills={pills}
                bookmarks={bookmarks}
                onToggleBookmark={toggleBookmark}
                onOpenShare={(p) => setSharePill(p)}
                calendar={calendar}
              />
            )}

            {/* Tab: Anomalies & 107 Trivia */}
            {currentTab === 'anomalies' && (
              <AnomaliesView
                anomalies={anomalies}
                onOpenShare={(p) => setSharePill(p)}
              />
            )}

            {/* Tab: What If Cognitive Assistant */}
            {currentTab === 'whatif' && (
              <SearchWhatIf
                pills={pills}
                anomalies={anomalies}
                circuits={circuits}
                drivers={drivers}
                apiKey={apiKey}
                setApiKey={setApiKey}
                openSettings={() => setSettingsOpen(true)}
              />
            )}

            {/* Tab: Lineages */}
            {currentTab === 'lineages' && (
              <LineageView lineages={lineages} />
            )}

            {/* Tab: DB Drivers & Circuits */}
            {currentTab === 'db' && (
              <DriversCircuitsView
                drivers={drivers}
                circuits={circuits}
              />
            )}

            {/* Tab: Bookmarks */}
            {currentTab === 'bookmarks' && (
              <div className="space-y-6 pb-20">
                <div className="flex items-center justify-between pb-3 border-b border-white/10">
                  <div className="flex items-center gap-2">
                    <Bookmark className="w-5 h-5 text-red-500 fill-red-500" />
                    <h2 className="font-f1-display font-black text-2xl text-white">
                      Pillole Salvate
                    </h2>
                  </div>
                  <span className="text-xs text-slate-400 font-mono">
                    {bookmarkedPills.length} elementi salvati
                  </span>
                </div>

                {bookmarkedPills.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {bookmarkedPills.map((pill) => (
                      <PillCard
                        key={pill.id}
                        pill={pill}
                        isBookmarked={true}
                        onToggleBookmark={toggleBookmark}
                        onOpenShare={(p) => setSharePill(p)}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="glass-panel rounded-2xl p-12 text-center space-y-3">
                    <Bookmark className="w-10 h-10 text-slate-600 mx-auto" />
                    <h4 className="font-f1-display font-bold text-lg text-white">Nessuna pillola salvata</h4>
                    <p className="text-slate-400 text-xs max-w-sm mx-auto">
                      Tocca l'icona del segnalibro su qualsiasi pillola o anomalia per ritrovarla rapidamente qui.
                    </p>
                    <button
                      onClick={() => setCurrentTab('feed')}
                      className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-colors"
                    >
                      Torna al Feed
                    </button>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>

      {/* Mobile-First Bottom Navigation Bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 glass-panel border-t border-white/10 py-1.5 px-3">
        <div className="max-w-md mx-auto flex items-center justify-around">
          <button
            onClick={() => setCurrentTab('feed')}
            className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-all ${
              currentTab === 'feed'
                ? 'text-red-500 scale-105'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Flame className="w-5 h-5" />
            <span className="text-[10px] font-bold font-f1-display tracking-tight">Pillole</span>
          </button>

          <button
            onClick={() => setCurrentTab('anomalies')}
            className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-all ${
              currentTab === 'anomalies'
                ? 'text-purple-400 scale-105'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-5 h-5" />
            <span className="text-[10px] font-bold font-f1-display tracking-tight">Anomalie</span>
          </button>

          <button
            onClick={() => setCurrentTab('whatif')}
            className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-all ${
              currentTab === 'whatif'
                ? 'text-indigo-400 scale-105'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <HelpCircle className="w-5 h-5" />
            <span className="text-[10px] font-bold font-f1-display tracking-tight">What If</span>
          </button>

          <button
            onClick={() => setCurrentTab('lineages')}
            className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-all ${
              currentTab === 'lineages'
                ? 'text-teal-400 scale-105'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <GitBranch className="w-5 h-5" />
            <span className="text-[10px] font-bold font-f1-display tracking-tight">Lignaggi</span>
          </button>

          <button
            onClick={() => setCurrentTab('db')}
            className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-all ${
              currentTab === 'db'
                ? 'text-red-400 scale-105'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Compass className="w-5 h-5" />
            <span className="text-[10px] font-bold font-f1-display tracking-tight">Database</span>
          </button>
        </div>
      </nav>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        apiKey={apiKey}
        setApiKey={setApiKey}
        pillsCount={pills.length}
        anomaliesCount={anomalies.length}
      />

      {/* Social Share Modal */}
      <SocialShareModal
        pill={sharePill}
        onClose={() => setSharePill(null)}
      />
    </div>
  );
}
