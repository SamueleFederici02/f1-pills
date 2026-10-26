import React, { useState } from 'react';
import { 
  X, 
  Key, 
  ExternalLink, 
  Smartphone, 
  ShieldCheck, 
  Trash2, 
  Check, 
  RefreshCw,
  HardDrive
} from 'lucide-react';

export default function SettingsModal({ 
  isOpen, 
  onClose, 
  apiKey, 
  setApiKey,
  pillsCount,
  anomaliesCount
}) {
  const [inputKey, setInputKey] = useState(apiKey || '');
  const [saved, setSaved] = useState(false);

  if (!isOpen) return null;

  const handleSaveKey = () => {
    setApiKey(inputKey.trim());
    if (inputKey.trim()) {
      localStorage.setItem('f1_pills_gemini_key', inputKey.trim());
    } else {
      localStorage.removeItem('f1_pills_gemini_key');
    }
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleClearKey = () => {
    setInputKey('');
    setApiKey('');
    localStorage.removeItem('f1_pills_gemini_key');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-[#0f131c] border border-white/10 rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-2xl p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div>
            <h3 className="font-f1-display font-black text-xl text-white">
              Impostazioni & Info App
            </h3>
            <p className="text-xs text-slate-400">Personalizzazione, Chiavi AI e Installazione</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Section 1: BYOK Gemini Key */}
        <div className="space-y-3 glass-panel p-4 rounded-xl border border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-yellow-400" />
              <h4 className="font-f1-display font-bold text-white text-sm">
                Chiave Google Gemini (Opzionale)
              </h4>
            </div>
            <a
              href="https://aistudio.google.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
            >
              <span>Ottieni gratis</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Per abilitare l'assistente conversazionale libero <strong>"What If"</strong>, puoi inserire la tua chiave gratuita personale di Google AI Studio. Viene salvata <strong>solo nel tuo browser</strong> (localStorage) e non viaggia mai su server esterni.
          </p>

          <div className="flex items-center gap-2">
            <input
              type="password"
              value={inputKey}
              onChange={(e) => setInputKey(e.target.value)}
              placeholder="Incolla la tua chiave AI Studio (AIzaSy...)"
              className="flex-1 bg-[#121620] border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-red-500 font-mono"
            />
            <button
              onClick={handleSaveKey}
              className="px-3.5 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-colors"
            >
              {saved ? <Check className="w-4 h-4" /> : 'Salva'}
            </button>
            {apiKey && (
              <button
                onClick={handleClearKey}
                className="p-2 rounded-xl bg-white/5 hover:bg-red-950/40 border border-white/10 text-slate-400 hover:text-red-400"
                title="Rimuovi chiave salvata"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Section 2: PWA Installation Guide */}
        <div className="space-y-3 glass-panel p-4 rounded-xl border border-white/10">
          <div className="flex items-center gap-2">
            <Smartphone className="w-4 h-4 text-emerald-400" />
            <h4 className="font-f1-display font-bold text-white text-sm">
              Come Installare su Smartphone (PWA)
            </h4>
          </div>

          <div className="space-y-2 text-xs text-slate-300">
            <div className="p-2.5 rounded-lg bg-black/40 border border-white/5 space-y-1">
              <span className="font-bold text-slate-200">📱 iPhone (Safari):</span>
              <p className="text-slate-400">
                Tocca l'icona di condivisione <strong className="text-white">Condividi</strong> in basso nel browser e seleziona <strong className="text-white">"Aggiungi a schermata Home"</strong>.
              </p>
            </div>

            <div className="p-2.5 rounded-lg bg-black/40 border border-white/5 space-y-1">
              <span className="font-bold text-slate-200">🤖 Android (Chrome):</span>
              <p className="text-slate-400">
                Tocca i tre puntini in alto a destra e seleziona <strong className="text-white">"Installa app"</strong> o <strong className="text-white">"Aggiungi a schermata Home"</strong>.
              </p>
            </div>
          </div>
        </div>

        {/* Section 3: Privacy & Offline Info */}
        <div className="space-y-2 glass-panel p-4 rounded-xl border border-white/10 text-xs text-slate-400">
          <div className="flex items-center gap-2 text-slate-200 font-bold mb-1">
            <ShieldCheck className="w-4 h-4 text-blue-400" />
            <span>Privacy & Conformità GDPR Totale</span>
          </div>
          <p>
            Questa applicazione è <strong>100% offline-first</strong>: nessun tracciamento di terze parti, nessun cookie banner fastidioso, nessun account richiesto.
          </p>
          <div className="pt-2 flex items-center justify-between font-mono text-[11px] text-slate-500 border-t border-white/5">
            <span>Database: {pillsCount} pillole &bull; {anomaliesCount} anomalie</span>
            <span>Versione 1.0 (2026)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
