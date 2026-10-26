import React, { useRef, useState } from 'react';
import { toPng } from 'html-to-image';
import { X, Share2, Download, Copy, Check, Sparkles, Flag, Flame } from 'lucide-react';

export default function SocialShareModal({ pill, onClose }) {
  const cardRef = useRef(null);
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!pill) return null;

  const handleShareImage = async () => {
    if (!cardRef.current) return;
    setDownloading(true);

    try {
      const dataUrl = await toPng(cardRef.current, { quality: 0.95, pixelRatio: 2 });
      
      // Try Web Share API with file
      if (navigator.share && navigator.canShare) {
        const blob = await (await fetch(dataUrl)).blob();
        const file = new File([blob], `f1-pill-${pill.id || 'stat'}.png`, { type: 'image/png' });
        
        if (navigator.canShare({ files: [file] })) {
          await navigator.share({
            title: pill.title,
            text: `${pill.title} — F1 Stats Pills (f1pills.web.app)`,
            files: [file]
          });
          setDownloading(false);
          return;
        }
      }

      // Fallback: download file directly
      const link = document.createElement('a');
      link.download = `f1-pill-${pill.id || 'card'}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error("Errore generazione card:", err);
      // Copy text fallback
      handleCopyText();
    } finally {
      setDownloading(false);
    }
  };

  const handleCopyText = () => {
    const text = `🏁 F1 PILLS: ${pill.title}\n${pill.subtext}\n\n👉 Scopri di più su f1pills.web.app`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-[#0f131c] border border-white/10 rounded-2xl max-w-md w-full overflow-hidden shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <Share2 className="w-4 h-4 text-red-500" />
            <h3 className="font-f1-display font-bold text-white text-base">
              Condividi Pillola Grafica
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* The Card Node To Capture */}
        <div className="p-4 flex justify-center">
          <div 
            ref={cardRef}
            className="w-full bg-gradient-to-br from-[#0c0e14] via-[#141924] to-[#0a0c10] border-2 border-red-600/40 rounded-2xl p-6 text-white shadow-2xl relative overflow-hidden"
          >
            {/* Watermark branding */}
            <div className="flex items-center justify-between mb-4 border-b border-white/10 pb-3">
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 rounded bg-red-600 flex items-center justify-center font-black text-xs">
                  F1
                </div>
                <span className="font-f1-display font-black tracking-tight text-sm text-white">
                  F1 <span className="text-red-500">PILLS</span>
                </span>
              </div>
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">
                VERIFIED FACT
              </span>
            </div>

            {/* Badge */}
            {pill.badge && (
              <div className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-red-600/30 text-red-300 border border-red-500/40 mb-3 font-f1-display">
                {pill.badge}
              </div>
            )}

            {/* Title */}
            <h2 className="font-f1-display font-black text-xl sm:text-2xl text-white leading-tight mb-3">
              {pill.title}
            </h2>

            {/* Subtext */}
            <p className="text-slate-300 text-xs sm:text-sm leading-relaxed mb-6 font-normal">
              {pill.subtext}
            </p>

            {/* Bottom branding footer */}
            <div className="pt-3 border-t border-white/10 flex items-center justify-between text-[10px] text-slate-400 font-mono">
              <span className="flex items-center gap-1">
                <Flame className="w-3 h-3 text-red-500" />
                <span>f1pills.web.app</span>
              </span>
              <span>1950 — 2026</span>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="p-4 pt-0 grid grid-cols-2 gap-3">
          <button
            onClick={handleCopyText}
            className="flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-white text-xs font-semibold transition-colors"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copiato!' : 'Copia Testo'}</span>
          </button>

          <button
            onClick={handleShareImage}
            disabled={downloading}
            className="flex items-center justify-center gap-2 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-all shadow-lg shadow-red-900/40"
          >
            {downloading ? (
              <span>Generazione...</span>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Salva Card / Condividi</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
