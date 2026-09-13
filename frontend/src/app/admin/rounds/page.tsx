"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { fetchApi } from '@/lib/api';
import { Shield, Play, Lock, CheckCircle2, Clock, RotateCcw } from 'lucide-react';

interface RoundItem {
  id: number;
  round_number: number;
  title: string;
  description: string;
  duration_minutes: number;
  max_marks: number;
  status: string;
}

export default function AdminRoundsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [rounds, setRounds] = useState<RoundItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && (!user || user.role !== 'admin')) {
      router.push('/admin/login');
      return;
    }
    if (user && user.role === 'admin') {
      loadRounds();
    }
  }, [user, isLoading, router]);

  const loadRounds = async () => {
    try {
      const data = await fetchApi('/rounds');
      setRounds(data);
    } catch (e) {
      console.error('Failed to load rounds:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (roundId: number, status: string) => {
    try {
      await fetchApi(`/admin/rounds/${roundId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status }),
      });
      loadRounds();
    } catch (e) {
      console.error('Failed to update round status:', e);
    }
  };

  if (isLoading || loading) {
    return <div className="py-20 text-center text-purple-400 font-mono animate-pulse">Loading Round Controls...</div>;
  }

  return (
    <div className="space-y-8 py-4">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-extrabold text-white">Round Control Center</h1>
        <p className="text-sm text-gray-400 mt-1">Manage round availability, status transitions, and durations.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {rounds.map((rnd) => (
          <div key={rnd.id} className="bg-gray-900 border border-gray-800 rounded-3xl p-6 flex flex-col justify-between shadow-2xl space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                <span className="text-xs font-mono font-bold text-purple-400">ROUND 0{rnd.round_number}</span>
                <span className={`px-3 py-1 text-xs font-mono font-bold rounded-full border ${
                  rnd.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-400 border-emerald-800' : 'bg-gray-800 text-gray-400 border-gray-700'
                }`}>
                  {rnd.status}
                </span>
              </div>

              <div>
                <h3 className="text-xl font-bold text-white mb-1">{rnd.title}</h3>
                <p className="text-xs text-gray-400 leading-relaxed">{rnd.description}</p>
              </div>

              <div className="text-xs font-mono text-gray-400 space-y-1">
                <div>Duration: <strong className="text-white">{rnd.duration_minutes} Minutes</strong></div>
                <div>Max Score: <strong className="text-white">{rnd.max_marks} Marks</strong></div>
              </div>
            </div>

            <div className="space-y-2 pt-4 border-t border-gray-800">
              <button
                onClick={() => handleUpdateStatus(rnd.id, 'ACTIVE')}
                disabled={rnd.status === 'ACTIVE'}
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2"
              >
                <Play className="w-3.5 h-3.5 fill-white" /> Start / Activate Round
              </button>

              <button
                onClick={() => handleUpdateStatus(rnd.id, 'LOCKED')}
                disabled={rnd.status === 'LOCKED'}
                className="w-full py-2.5 bg-amber-600 hover:bg-amber-500 disabled:opacity-40 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2"
              >
                <Lock className="w-3.5 h-3.5" /> Pause / Lock Round
              </button>

              <button
                onClick={() => handleUpdateStatus(rnd.id, 'COMPLETED')}
                disabled={rnd.status === 'COMPLETED'}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2"
              >
                <CheckCircle2 className="w-3.5 h-3.5" /> Complete & Finalize
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
