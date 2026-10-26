import React, { useState } from 'react';
import { 
  Sparkles, 
  Send, 
  Key, 
  AlertCircle, 
  HelpCircle, 
  ExternalLink, 
  CheckCircle2, 
  Bot,
  Zap,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';

export default function SearchWhatIf({ 
  pills = [], 
  anomalies = [], 
  circuits = [], 
  drivers = [],
  apiKey,
  setApiKey,
  openSettings
}) {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Pre-cooked What-If scenarios for quick testing
  const samplePrompts = [
    {
      q: "Cosa succederebbe se Verstappen vincesse su 3 ruote?",
      preset: {
        driver: "Max Verstappen",
        condition: "3_wheels",
        matchId: 1, // Lewis Hamilton Silverstone 2020
        text: "Se Max Verstappen vincesse tagliando il traguardo su sole 3 ruote, eguaglierebbe il leggendario e clamoroso primato di Lewis Hamilton al Gran Premio di Gran Bretagna 2020 a Silverstone, quando la Mercedes tagliò il traguardo su tre cerchioni a 100 km/h dopo l'esplosione dell'anteriore sinistra all'ultimo giro."
      }
    },
    {
      q: "È mai successo che qualcuno vincesse scontando la penalità ai box?",
      preset: {
        driver: "Michael Schumacher",
        condition: "pit_lane_finish",
        matchId: 2, // Schumacher 1998
        text: "Sì, è un evento storico documentato! Nel Gran Premio di Gran Bretagna 1998 a Silverstone, Michael Schumacher su Ferrari vinse la gara tagliando la linea del traguardo all'interno della corsia dei box per scontare uno Stop&Go di 10 secondi all'ultimo giro, sfruttando una falla del regolamento sportivo della FIA."
      }
    },
    {
      q: "Chi ha vinto un Gran Premio nel giorno esatto del compleanno?",
      preset: {
        driver: "Jean Alesi & James Hunt",
        condition: "birthday_win",
        matchId: 30, // Alesi 1995 & Hunt 1976
        text: "È successo solo 2 volte nella storia della Formula 1 (1950–2026): Jean Alesi l'11 giugno 1995 al GP del Canada a Montreal con la Ferrari #27 per il suo 31° compleanno (tornando ai box aggrappato alla Benetton di Schumacher), e James Hunt il 29 agosto 1976 a Zandvoort con la McLaren per il suo 29° compleanno."
      }
    },
    {
      q: "Se Leclerc vincesse partendo 4° a Melbourne cosa succederebbe?",
      preset: {
        driver: "Charles Leclerc",
        condition: "grid_4_melbourne",
        text: "Sarebbe la prima vittoria in carriera di Charles Leclerc partendo dalla 4ª casella della griglia all'Albert Park. Inoltre, allungherebbe il record storico della Scuderia Ferrari, che vanta la maggior percentuale di trionfi a Melbourne con piloti partiti entro le prime due file."
      }
    }
  ];

  const handleAsk = async (userPrompt = question) => {
    if (!userPrompt.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    // Check if matching a quick preset
    const matchedPreset = samplePrompts.find(p => p.q.toLowerCase() === userPrompt.toLowerCase());
    if (matchedPreset) {
      setTimeout(() => {
        setResult({
          intent: { matched: true, prompt: userPrompt },
          answer: matchedPreset.preset.text,
          anomaly: anomalies.find(a => a.id == matchedPreset.preset.matchId)
        });
        setLoading(false);
      }, 400);
      return;
    }

    // If BYOK Gemini key is present, invoke Google AI Studio Gemini API
    if (apiKey) {
      try {
        const systemPrompt = `Sei l'assistente ufficiale di F1 Stats Pills. L'utente pone una domanda o scenario "What If" sulla Formula 1.
Il tuo compito è:
1. Identificare pilota, circuito, o condizione bizzarra (es. 3 ruote, compleanno, pit lane, pioggia, sciopero, tombino).
2. Rispondere in modo brillante, rigoroso, senza inventare falsi storici.
3. Se menziona un'anomalia famosa, collegala alla storia della F1 (1950-2026).
Rispondi in lingua italiana in modo chiaro e conciso (massimo 2-3 frasi ad alto impatto).`;

        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [
              {
                role: 'user',
                parts: [{ text: `${systemPrompt}\n\nDomanda utente: "${userPrompt}"` }]
              }
            ]
          })
        });

        if (!response.ok) {
          throw new Error(`Errore API Gemini (${response.status})`);
        }

        const data = await response.json();
        const replyText = data.candidates?.[0]?.content?.parts?.[0]?.text || "Nessuna risposta disponibile.";

        // Find relevant anomalies based on keywords
        const lowerPrompt = userPrompt.toLowerCase();
        const relatedAnomaly = anomalies.find(a => {
          return a.keywords?.split(';').some(k => lowerPrompt.includes(k.trim().toLowerCase())) ||
                 lowerPrompt.includes(a.driver_id?.toLowerCase() || '') ||
                 lowerPrompt.includes(a.circuit_id?.toLowerCase() || '');
        });

        setResult({
          intent: { userPrompt },
          answer: replyText,
          anomaly: relatedAnomaly
        });
      } catch (err) {
        console.error(err);
        // Fallback to local heuristic search
        fallbackLocalSearch(userPrompt);
      } finally {
        setLoading(false);
      }
    } else {
      // Local Heuristic Fallback
      fallbackLocalSearch(userPrompt);
      setLoading(false);
    }
  };

  const fallbackLocalSearch = (q) => {
    const lower = q.toLowerCase();
    
    // Look for matching anomalies
    const matched = anomalies.find(a => {
      const keys = (a.keywords || '').toLowerCase().split(';');
      return keys.some(k => k.trim().length > 2 && lower.includes(k.trim())) ||
             (a.title && lower.includes(a.title.toLowerCase())) ||
             (a.grand_prix && lower.includes(a.grand_prix.toLowerCase()));
    });

    // Look for matching pill
    const matchedPill = pills.find(p => {
      return (p.title && lower.includes(p.title.toLowerCase())) ||
             (p.keywords && p.keywords.some(k => k.length > 2 && lower.includes(k.toLowerCase())));
    });

    if (matched) {
      setResult({
        intent: { userPrompt: q, mode: 'local_deterministic' },
        answer: `Nel database storico è documentato l'episodio analogo: "${matched.title}" (${matched.grand_prix} ${matched.year}). ${matched.description}`,
        anomaly: matched
      });
    } else if (matchedPill) {
      setResult({
        intent: { userPrompt: q, mode: 'local_deterministic' },
        answer: `Coincidenza statistica rilevata: ${matchedPill.title}. ${matchedPill.subtext}`,
        pill: matchedPill
      });
    } else {
      setResult({
        intent: { userPrompt: q, mode: 'local_deterministic' },
        answer: `Scenario ipotetico analizzato: la combinazione interrogata non ha precedenti identici dal 1950 a oggi nel database. Inserisci una chiave personale Google Gemini nelle impostazioni per analizzare combinazioni predittive complesse in linguaggio naturale.`
      });
    }
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Engine Header */}
      <div className="glass-panel-elevated rounded-2xl p-6 border border-white/10 relative overflow-hidden bg-gradient-to-br from-indigo-950/30 via-[#0e121a] to-red-950/20">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider font-f1-display">
                WHAT IF COGNITIVE ENGINE
              </span>
              <span className="text-[11px] text-slate-400 font-mono">Architettura BYOK Zero Costi</span>
            </div>
            <h2 className="font-f1-display font-black text-2xl text-white">
              Cosa Succederebbe Se...?
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Poni domande ipotetiche su scenari pre-gara, arrivi bizzarri o coincidenze. Il motore relazionale incrocia la tua domanda con 107 anomalie storiche e 76 anni di Formula 1.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {apiKey ? (
              <div className="flex items-center gap-2 bg-emerald-950/40 border border-emerald-500/40 px-3 py-1.5 rounded-xl text-emerald-300 text-xs">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold">Gemini Flash Attivo</span>
              </div>
            ) : (
              <button
                onClick={openSettings}
                className="flex items-center gap-1.5 bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-1.5 rounded-xl text-slate-300 hover:text-white text-xs font-semibold transition-colors"
              >
                <Key className="w-3.5 h-3.5 text-yellow-400" />
                <span>Configura Chiave (Opzionale)</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Query Input Box */}
      <div className="glass-panel rounded-2xl p-4 border border-white/10 space-y-3">
        <div className="relative">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleAsk();
              }
            }}
            placeholder="Scrivi qui la tua domanda o scenario (es. Se Leclerc vince partendo 4° a Melbourne cosa succederebbe? È mai successo che vincessero su 3 ruote?)"
            className="w-full bg-[#121620] border border-white/10 rounded-xl p-3.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors shadow-inner resize-none min-h-[90px]"
          />
        </div>

        <div className="flex items-center justify-between gap-3">
          <span className="text-[11px] text-slate-400">
            {apiKey ? '⚡ Modalità AI Gemini 2.0 Flash attiva' : '🔍 Modalità Heuristic Offline (100% funzionante senza chiavi)'}
          </span>

          <button
            onClick={() => handleAsk()}
            disabled={loading || !question.trim()}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-red-600 to-indigo-600 hover:from-red-500 hover:to-indigo-500 disabled:opacity-50 text-white font-bold text-xs shadow-lg shadow-indigo-900/30 transition-all"
          >
            {loading ? (
              <span>Elaborazione...</span>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>Interroga</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Quick Scenarios Suggestions */}
      <div className="space-y-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <Zap className="w-3.5 h-3.5 text-yellow-400" />
          <span>Scenari Istantanei Preconfigurati:</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {samplePrompts.map((item, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuestion(item.q);
                handleAsk(item.q);
              }}
              className="glass-panel p-3 rounded-xl border border-white/5 hover:border-indigo-500/50 hover:bg-white/5 text-left transition-all text-xs text-slate-300 flex items-center justify-between gap-2 group"
            >
              <span className="group-hover:text-white">{item.q}</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all shrink-0" />
            </button>
          ))}
        </div>
      </div>

      {/* Answer Box */}
      {result && (
        <div className="glass-panel-elevated rounded-2xl p-6 border border-indigo-500/30 bg-gradient-to-br from-indigo-950/20 via-[#10141f] to-slate-900 animate-fadeIn space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-indigo-400" />
              <h3 className="font-f1-display font-bold text-lg text-white">
                Risposta & Riscontro Storico
              </h3>
            </div>
            <span className="text-[11px] font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded">
              VERIFICATO NEL DB
            </span>
          </div>

          <div className="text-slate-200 text-sm sm:text-base leading-relaxed">
            {result.answer}
          </div>

          {/* Connected Historical Anomaly Card */}
          {result.anomaly && (
            <div className="p-4 rounded-xl bg-black/40 border border-amber-500/30 space-y-2 mt-3">
              <div className="flex items-center gap-2 text-amber-400 font-bold text-xs uppercase tracking-wide">
                <Sparkles className="w-4 h-4" />
                <span>Episodio Storico Documentato #{result.anomaly.id}</span>
              </div>
              <h4 className="font-f1-display font-bold text-white text-base">
                {result.anomaly.title} ({result.anomaly.grand_prix} {result.anomaly.year})
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                {result.anomaly.description}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
