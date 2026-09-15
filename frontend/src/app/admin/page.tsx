"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { fetchApi } from '@/lib/api';
import { Shield, Lock, Power, Users, FileCode, Trophy, Settings, HelpCircle, CheckCircle, AlertTriangle, Activity, RefreshCw } from 'lucide-react';

interface Stats {
  total_participants: number;
  active_participants: number;
  r1_completed: number;
  r2_completed: number;
  r3_completed: number;
  total_submissions: number;
  average_score: number;
  highest_score: number;
}

interface ActivityLogItem {
  id: number;
  user_id: number;
  user_email?: string;
  event_type: string;
  round_id?: number;
  question_id?: number;
  timestamp: string;
  metadata_json?: string;
  ip_address?: string;
}

export default function AdminConsolePage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState<Stats | null>(null);
  const [activities, setActivities] = useState<ActivityLogItem[]>([]);
  const [maintenance, setMaintenance] = useState(false);
  const [locked, setLocked] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && (!user || user.role !== 'admin')) {
      router.push('/admin/login');
      return;
    }
    if (user && user.role === 'admin') {
      loadAdminOverview();
      loadLiveActivity();

      // Directives: 3-second polling for real-time monitoring
      const interval = setInterval(() => {
        loadAdminOverview();
        loadLiveActivity();
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [user, isLoading, router]);

  const loadAdminOverview = async () => {
    try {
      const data = await fetchApi('/admin/dashboard');
      setStats(data);

      const st = await fetchApi('/admin/settings');
      setMaintenance(st.maintenance_mode);
      setLocked(st.lock_all_participants);
    } catch (e: any) {
      console.error('Failed to load admin overview:', e);
      if (e?.message?.includes('privileges required') || e?.message?.includes('authenticated')) {
        router.push('/admin/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadLiveActivity = async () => {
    try {
      const data = await fetchApi('/admin/activity?limit=30');
      setActivities(data);
    } catch (e: any) {
      console.error('Failed to load live activity stream:', e);
      if (e?.message?.includes('privileges required') || e?.message?.includes('authenticated')) {
        router.push('/admin/login');
      }
    }
  };

  const handleToggleEmergencyLock = async () => {
    try {
      const newLock = !locked;
      await fetchApi(`/admin/emergency-lock?lock=${newLock}`, { method: 'POST' });
      setLocked(newLock);
    } catch (e) {
      console.error('Lock toggle failed:', e);
    }
  };

  const handleToggleMaintenanceMode = async () => {
    try {
      const newMaint = !maintenance;
      await fetchApi(`/admin/maintenance-mode?enable=${newMaint}`, { method: 'POST' });
      setMaintenance(newMaint);
    } catch (e) {
      console.error('Maintenance toggle failed:', e);
    }
  };

  if (isLoading || loading) {
    return <div className="py-20 text-center text-purple-400 font-mono animate-pulse">Loading Admin Control Console...</div>;
  }

  return (
    <div className="space-y-8 py-4">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-purple-950/50 via-gray-900 to-indigo-950/50 border border-purple-800/50 rounded-3xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-2xl">
        <div>
          <span className="text-xs font-mono font-bold text-purple-400 uppercase tracking-wider">Engineering Day 2026</span>
          <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
            <Shield className="w-8 h-8 text-purple-400" /> Administrator Console
          </h1>
          <p className="text-xs text-gray-400 mt-1">Global Competition Control Panel & Real-time Activity Monitoring</p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 text-xs font-semibold">
          <Link href="/admin/rounds" className="px-3.5 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-xl border border-gray-700">
            Rounds
          </Link>
          <Link href="/admin/questions" className="px-3.5 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-xl border border-gray-700">
            Questions
          </Link>
          <Link href="/admin/participants" className="px-3.5 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-xl border border-gray-700">
            Participants
          </Link>
          <Link href="/admin/submissions" className="px-3.5 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-xl border border-gray-700">
            Submissions
          </Link>
          <Link href="/admin/settings" className="px-3.5 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl font-bold shadow-md shadow-purple-600/20">
            Settings & Backup
          </Link>
        </div>
      </div>

      {/* Emergency Control Section */}
      <div className="bg-gray-900 border-2 border-red-900/60 rounded-3xl p-6 shadow-2xl space-y-4">
        <div className="flex items-center gap-3 text-red-400">
          <AlertTriangle className="w-6 h-6" />
          <h2 className="text-lg font-bold text-white">Emergency Contest Controls</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button
            onClick={handleToggleEmergencyLock}
            className={`p-4 rounded-2xl border font-bold flex items-center justify-between transition-all ${
              locked
                ? 'bg-red-950/80 border-red-600 text-red-200'
                : 'bg-gray-950 border-gray-800 text-gray-300 hover:border-red-600/50'
            }`}
          >
            <div className="flex items-center gap-3">
              <Lock className={`w-6 h-6 ${locked ? 'text-red-400' : 'text-gray-500'}`} />
              <div className="text-left">
                <div className="text-sm">Lock All Participants</div>
                <div className="text-xs font-normal text-gray-400">
                  {locked ? 'ACTIVE: All actions blocked' : 'DISABLED: Normal competition'}
                </div>
              </div>
            </div>
            <span className={`px-3 py-1 text-xs font-mono rounded-lg border ${locked ? 'bg-red-600 text-white' : 'bg-gray-800 text-gray-400'}`}>
              {locked ? 'LOCKED' : 'LOCK ALL'}
            </span>
          </button>

          <button
            onClick={handleToggleMaintenanceMode}
            className={`p-4 rounded-2xl border font-bold flex items-center justify-between transition-all ${
              maintenance
                ? 'bg-purple-950/80 border-purple-600 text-purple-200'
                : 'bg-gray-950 border-gray-800 text-gray-300 hover:border-purple-600/50'
            }`}
          >
            <div className="flex items-center gap-3">
              <Power className={`w-6 h-6 ${maintenance ? 'text-purple-400' : 'text-gray-500'}`} />
              <div className="text-left">
                <div className="text-sm">Maintenance Mode</div>
                <div className="text-xs font-normal text-gray-400">
                  {maintenance ? 'ACTIVE: Portal offline for students' : 'DISABLED: Portal open'}
                </div>
              </div>
            </div>
            <span className={`px-3 py-1 text-xs font-mono rounded-lg border ${maintenance ? 'bg-purple-600 text-white' : 'bg-gray-800 text-gray-400'}`}>
              {maintenance ? 'MAINTENANCE' : 'TOGGLE'}
            </span>
          </button>
        </div>
      </div>

      {/* System Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 shadow-xl">
          <span className="text-xs font-mono text-gray-400 uppercase font-semibold">Total Participants</span>
          <div className="text-3xl font-extrabold text-white mt-1">{stats?.total_participants}</div>
          <span className="text-xs text-emerald-400 mt-1 block">{stats?.active_participants} Active</span>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 shadow-xl">
          <span className="text-xs font-mono text-gray-400 uppercase font-semibold">Total Submissions</span>
          <div className="text-3xl font-extrabold text-blue-400 mt-1">{stats?.total_submissions}</div>
          <span className="text-xs text-gray-500 mt-1 block">Judge0 Evaluated</span>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 shadow-xl">
          <span className="text-xs font-mono text-gray-400 uppercase font-semibold">Average Score</span>
          <div className="text-3xl font-extrabold text-purple-400 mt-1">{stats?.average_score}</div>
          <span className="text-xs text-gray-500 mt-1 block">Across all rounds</span>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 shadow-xl">
          <span className="text-xs font-mono text-gray-400 uppercase font-semibold">Highest Score</span>
          <div className="text-3xl font-extrabold text-amber-400 mt-1">{stats?.highest_score}</div>
          <span className="text-xs text-amber-500/80 mt-1 block">Current Leader</span>
        </div>
      </div>

      {/* Real-time Activity Feed Stream */}
      <div className="bg-gray-900 border border-gray-800 rounded-3xl p-6 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-400 animate-pulse" />
            <h3 className="text-lg font-bold text-white">Live Activity Feed Stream</h3>
          </div>
          <span className="text-xs font-mono text-emerald-400 font-semibold flex items-center gap-1.5">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-400" /> Polling Live (3s)
          </span>
        </div>

        <div className="bg-[#0d1117] border border-gray-800 rounded-2xl p-4 font-mono text-xs max-h-72 overflow-y-auto space-y-2">
          {activities.length === 0 ? (
            <span className="text-gray-500">No competition activities recorded yet.</span>
          ) : (
            activities.map((act) => {
              const timeStr = act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : '';
              let badgeColor = "text-blue-400";
              if (act.event_type.includes("AUTO") || act.event_type.includes("TAB")) badgeColor = "text-red-400 font-bold";
              if (act.event_type.includes("SUBMIT")) badgeColor = "text-emerald-400 font-bold";

              return (
                <div key={act.id} className="flex items-start justify-between border-b border-gray-900 pb-1.5 pt-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500 font-bold">[{timeStr}]</span>
                    <span className="text-white font-semibold">{act.user_email || `User #${act.user_id}`}</span>
                    <span className={`${badgeColor}`}>{act.event_type}</span>
                    {act.round_id && <span className="text-gray-400">(Round {act.round_id})</span>}
                  </div>
                  {act.metadata_json && (
                    <span className="text-gray-500 text-[11px] truncate max-w-xs">{act.metadata_json}</span>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Round Completion Metrics */}
      <div className="bg-gray-900 border border-gray-800 rounded-3xl p-6 shadow-xl space-y-4">
        <h3 className="text-lg font-bold text-white">Round Completion Statistics</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-gray-950 border border-gray-800 rounded-2xl p-4 flex items-center justify-between">
            <span className="text-xs font-mono text-gray-300 font-bold">Round 1 (Aptitude)</span>
            <span className="text-lg font-mono font-bold text-blue-400">{stats?.r1_completed} Completed</span>
          </div>

          <div className="bg-gray-950 border border-gray-800 rounded-2xl p-4 flex items-center justify-between">
            <span className="text-xs font-mono text-gray-300 font-bold">Round 2 (Debugging)</span>
            <span className="text-lg font-mono font-bold text-purple-400">{stats?.r2_completed} Completed</span>
          </div>

          <div className="bg-gray-950 border border-gray-800 rounded-2xl p-4 flex items-center justify-between">
            <span className="text-xs font-mono text-gray-300 font-bold">Round 3 (Coding)</span>
            <span className="text-lg font-mono font-bold text-emerald-400">{stats?.r3_completed} Completed</span>
          </div>
        </div>
      </div>
    </div>
  );
}
