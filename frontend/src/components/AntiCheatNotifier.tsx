"use client";

import { useEffect, useState } from 'react';
import { fetchApi } from '@/lib/api';
import { AlertTriangle, X } from 'lucide-react';

export default function AntiCheatNotifier() {
  const [warningOpen, setWarningOpen] = useState(false);
  const [warningCount, setWarningCount] = useState(0);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        logViolation("TAB_SWITCH", "Participant switched tab or minimized window.");
      }
    };

    const handleBlur = () => {
      logViolation("WINDOW_BLUR", "Participant window lost focus.");
    };

    window.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("blur", handleBlur);

    return () => {
      window.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("blur", handleBlur);
    };
  }, []);

  const logViolation = async (type: string, details: string) => {
    try {
      const res = await fetchApi("/violations", {
        method: "POST",
        body: JSON.stringify({ violation_type: type, details })
      });
      setWarningCount(res.total_violations || 1);
      setWarningOpen(true);
    } catch (e) {
      console.error("Failed to log anti-cheating violation:", e);
    }
  };

  if (!warningOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-gray-900 border-2 border-red-600 rounded-2xl p-6 max-w-md w-full shadow-2xl animate-shake">
        <div className="flex items-center gap-3 text-red-500 mb-3">
          <AlertTriangle className="w-8 h-8" />
          <h2 className="text-xl font-bold text-white">Cheating Warning Detected!</h2>
        </div>

        <p className="text-sm text-gray-300 mb-4 leading-relaxed">
          Leaving or switching away from the competition window has been detected and logged.
        </p>

        <div className="bg-red-950/50 border border-red-800 rounded-xl p-3 mb-6 text-center">
          <span className="text-xs font-mono text-red-300 font-semibold block uppercase">Total Violations Recorded</span>
          <span className="text-3xl font-extrabold text-red-400 font-mono">{warningCount}</span>
          <span className="text-xs text-red-400/80 block mt-1">Further violations may result in immediate disqualification.</span>
        </div>

        <button
          onClick={() => setWarningOpen(false)}
          className="w-full py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl transition-colors shadow-lg shadow-red-600/30 flex items-center justify-center gap-2"
        >
          <span>I Understand & Resume Competition</span>
        </button>
      </div>
    </div>
  );
}
