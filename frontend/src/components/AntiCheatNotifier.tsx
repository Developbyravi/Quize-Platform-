"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';
import { AlertTriangle, Lock } from 'lucide-react';

interface AntiCheatNotifierProps {
  roundId?: number;
  onAutoSubmitted?: () => void;
}

export default function AntiCheatNotifier({ roundId, onAutoSubmitted }: AntiCheatNotifierProps) {
  const router = useRouter();
  const [autoSubmitted, setAutoSubmitted] = useState(false);
  const [warningMessage, setWarningMessage] = useState('');

  useEffect(() => {
    const handleVisibilityChange = async () => {
      // Directives: The ONLY automatic tab-switch submission trigger is document.visibilityState === "hidden"
      if (document.visibilityState === "hidden" && roundId && !autoSubmitted) {
        try {
          // Log page hidden activity
          fetchApi("/activity", {
            method: "POST",
            body: JSON.stringify({ event_type: "PAGE_HIDDEN", round_id: roundId })
          }).catch(() => {});

          // Call authoritative auto-submit endpoint
          const res = await fetchApi(`/rounds/${roundId}/auto-submit`, {
            method: "POST"
          });

          setAutoSubmitted(true);
          setWarningMessage(res.message || "Your round has been automatically submitted because you left the competition tab.");
          if (onAutoSubmitted) onAutoSubmitted();
        } catch (e: any) {
          console.error("Auto-submit request failed:", e);
        }
      }
    };

    const handleBlur = () => {
      // Directives: window.blur must NOT trigger auto-submission.
      // It may only generate an optional lightweight activity event.
      if (roundId) {
        fetchApi("/activity", {
          method: "POST",
          body: JSON.stringify({ event_type: "WINDOW_BLUR", round_id: roundId })
        }).catch(() => {});
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("blur", handleBlur);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("blur", handleBlur);
    };
  }, [roundId, autoSubmitted, onAutoSubmitted]);

  if (!autoSubmitted) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-gray-900 border-2 border-red-600 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4 text-center">
        <div className="w-16 h-16 bg-red-950/80 border-2 border-red-600 rounded-full flex items-center justify-center mx-auto text-red-500 animate-pulse">
          <Lock className="w-8 h-8" />
        </div>

        <div className="space-y-1">
          <h2 className="text-xl font-extrabold text-white">Round Automatically Submitted</h2>
          <span className="text-xs font-mono font-bold text-red-400 uppercase tracking-wider">Tab Switch Violation Detected</span>
        </div>

        <p className="text-sm text-gray-300 leading-relaxed bg-red-950/40 border border-red-900/60 p-4 rounded-2xl">
          {warningMessage}
        </p>

        <button
          onClick={() => router.push('/dashboard')}
          className="w-full py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-red-600/30 text-sm"
        >
          Return to Dashboard
        </button>
      </div>
    </div>
  );
}
