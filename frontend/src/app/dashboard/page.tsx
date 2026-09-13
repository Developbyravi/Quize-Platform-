"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { fetchApi } from '@/lib/api';
import { Lock, Play, CheckCircle2, Clock, Trophy, AlertTriangle, ArrowRight } from 'lucide-react';

interface RoundItem {
  id: number;
  round_number: number;
  title: string;
  description: string;
  duration_minutes: number;
  max_marks: number;
  status: string; // LOCKED, UPCOMING, ACTIVE, COMPLETED
}

export default function ParticipantDashboard() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [rounds, setRounds] = useState<RoundItem[]>([]);
  const [error, setError] = useState<string>('');
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
      return;
    }
    if (user) {
      loadRounds();
    }
  }, [user, isLoading, router]);

  const loadRounds = async () => {
    try {
      const data = await fetchApi('/rounds');
      setRounds(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch round statuses.');
    } finally {
      setLoadingData(false);
    }
  };

  const handleEnterRound = (roundNumber: number) => {
    router.push(`/rounds/${roundNumber}`);
  };

  if (isLoading || loadingData) {
    return (
      <div className="py-20 text-center text-gray-400 font-mono animate-pulse">
        Loading contest dashboard...
      </div>
    );
  }

  return (
    <div className="space-y-8 py-4">
      {/* Participant Header Banner */}
      <div className="bg-gradient-to-r from-blue-900/40 via-gray-900 to-indigo-900/40 border border-blue-800/40 rounded-3xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div>
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-blue-400">Engineering Day 2026</span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Welcome, {user?.full_name}!
          </h1>
          <p className="text-sm text-gray-400 mt-1">Select an active competition round below to enter the portal.</p>
        </div>
        <button
          onClick={() => router.push('/leaderboard')}
          className="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-amber-300 font-semibold rounded-xl border border-gray-700 transition-colors flex items-center gap-2 text-sm shrink-0"
        >
          <Trophy className="w-4 h-4 text-amber-400" /> View Contest Leaderboard
        </button>
      </div>

      {error && (
        <div className="bg-red-950/80 border border-red-800 rounded-2xl p-4 text-red-300 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 3 Round Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {rounds.map((rnd) => {
          const isActive = rnd.status === 'ACTIVE';
          const isCompleted = rnd.status === 'COMPLETED';
          const isLocked = rnd.status === 'LOCKED';

          let statusBadgeClass = "bg-gray-800 text-gray-400 border-gray-700";
          if (isActive) statusBadgeClass = "bg-emerald-950 text-emerald-400 border-emerald-800 animate-pulse";
          if (isCompleted) statusBadgeClass = "bg-blue-950 text-blue-400 border-blue-800";
          if (isLocked) statusBadgeClass = "bg-gray-900 text-gray-500 border-gray-800";

          return (
            <div
              key={rnd.id}
              className={`bg-gray-900/80 border rounded-3xl p-6 flex flex-col justify-between transition-all ${
                isActive
                  ? 'border-blue-500/80 shadow-2xl shadow-blue-500/10'
                  : 'border-gray-800 opacity-90'
              }`}
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-extrabold text-blue-400 tracking-wider">
                    ROUND 0{rnd.round_number}
                  </span>
                  <span className={`px-3 py-1 text-xs font-mono font-bold rounded-full border ${statusBadgeClass}`}>
                    {rnd.status}
                  </span>
                </div>

                <div>
                  <h2 className="text-xl font-extrabold text-white mb-1">{rnd.title}</h2>
                  <p className="text-xs text-gray-400 leading-relaxed line-clamp-3">{rnd.description}</p>
                </div>

                <div className="flex items-center justify-between text-xs font-mono text-gray-400 pt-3 border-t border-gray-800">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-blue-400" /> {rnd.duration_minutes} Mins
                  </span>
                  <span>Max Score: <strong className="text-white">{rnd.max_marks}</strong></span>
                </div>
              </div>

              <div className="pt-6">
                {isActive ? (
                  <button
                    onClick={() => handleEnterRound(rnd.round_number)}
                    className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2 text-sm"
                  >
                    <Play className="w-4 h-4 fill-white" /> Enter Round {rnd.round_number}
                  </button>
                ) : isCompleted ? (
                  <button
                    disabled
                    className="w-full py-3 bg-gray-800 text-gray-400 font-semibold rounded-xl border border-gray-700 flex items-center justify-center gap-2 text-sm cursor-not-allowed"
                  >
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Completed
                  </button>
                ) : (
                  <button
                    disabled
                    className="w-full py-3 bg-gray-950 text-gray-600 font-semibold rounded-xl border border-gray-800 flex items-center justify-center gap-2 text-sm cursor-not-allowed"
                  >
                    <Lock className="w-4 h-4" /> Locked by Admin
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
