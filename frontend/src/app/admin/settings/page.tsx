"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { fetchApi } from '@/lib/api';
import { Settings, Database, Download, Shield, Eye, Lock, Save, AlertCircle } from 'lucide-react';

interface SettingsData {
  contest_title: string;
  subtitle: string;
  maintenance_mode: boolean;
  lock_all_participants: boolean;
  leaderboard_visible: boolean;
  leaderboard_frozen: boolean;
  max_cheating_warnings: number;
  max_participants: number;
  run_code_rate_limit_sec: number;
  submit_code_rate_limit_sec: number;
}

export default function AdminSettingsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [settings, setSettings] = useState<SettingsData>({
    contest_title: 'Engineering Day Coding Challenge',
    subtitle: 'Engineering Day 2026 — Coding Competition',
    maintenance_mode: false,
    lock_all_participants: false,
    leaderboard_visible: true,
    leaderboard_frozen: false,
    max_cheating_warnings: 3,
    max_participants: 100,
    run_code_rate_limit_sec: 3,
    submit_code_rate_limit_sec: 5,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isLoading && (!user || user.role !== 'admin')) {
      router.push('/admin/login');
      return;
    }
    if (user && user.role === 'admin') {
      loadSettings();
    }
  }, [user, isLoading, router]);

  const loadSettings = async () => {
    try {
      const data = await fetchApi('/admin/settings');
      setSettings(data);
    } catch (e) {
      console.error('Failed to load settings:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      await fetchApi('/admin/settings', {
        method: 'PUT',
        body: JSON.stringify(settings),
      });
      setMessage('Contest settings updated successfully.');
    } catch (err: any) {
      setMessage(err.message || 'Failed to update settings.');
    } finally {
      setSaving(false);
    }
  };

  const handleExportJSON = async () => {
    try {
      const data = await fetchApi('/admin/export?format=json');
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contest_backup_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
    } catch (e) {
      console.error('JSON Export failed:', e);
    }
  };

  const handleExportCSV = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('http://localhost:8000/api/admin/export?format=csv', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contest_results_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
    } catch (e) {
      console.error('CSV Export failed:', e);
    }
  };

  if (isLoading || loading) {
    return <div className="py-20 text-center text-purple-400 font-mono animate-pulse">Loading Contest Configurations...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <Settings className="w-8 h-8 text-purple-400" /> Contest Settings & Disaster Backup
        </h1>
        <p className="text-sm text-gray-400 mt-1">Global competition parameters, rate limiting, and database exports.</p>
      </div>

      {message && (
        <div className="bg-purple-950/80 border border-purple-800 rounded-xl p-3.5 text-purple-300 text-xs font-semibold">
          {message}
        </div>
      )}

      {/* Database Backup Section */}
      <div className="bg-gray-900 border border-gray-800 rounded-3xl p-6 shadow-2xl space-y-4">
        <div className="flex items-center gap-3 text-emerald-400">
          <Database className="w-6 h-6" />
          <h2 className="text-lg font-bold text-white">Database Backup & Results Export</h2>
        </div>
        <p className="text-xs text-gray-400">
          Export a complete JSON snapshot of all participants, submissions, and scores before or after the competition.
        </p>

        <div className="flex flex-wrap gap-4 pt-2">
          <button
            onClick={handleExportJSON}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-emerald-600/20"
          >
            <Download className="w-4 h-4" /> Download Complete DB Snapshot (JSON)
          </button>
          <button
            onClick={handleExportCSV}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-blue-600/20"
          >
            <Download className="w-4 h-4" /> Download Final Leaderboard (CSV)
          </button>
        </div>
      </div>

      {/* Settings Form */}
      <form onSubmit={handleSave} className="bg-gray-900 border border-gray-800 rounded-3xl p-6 shadow-2xl space-y-6">
        <h2 className="text-lg font-bold text-white border-b border-gray-800 pb-3">Global Contest Configurations</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">Contest Title</label>
            <input
              type="text"
              value={settings.contest_title}
              onChange={(e) => setSettings({ ...settings, contest_title: e.target.value })}
              className="w-full bg-gray-950 border border-gray-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">Subtitle</label>
            <input
              type="text"
              value={settings.subtitle}
              onChange={(e) => setSettings({ ...settings, subtitle: e.target.value })}
              className="w-full bg-gray-950 border border-gray-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">Run Code Rate Limit (Seconds)</label>
            <input
              type="number"
              value={settings.run_code_rate_limit_sec}
              onChange={(e) => setSettings({ ...settings, run_code_rate_limit_sec: Number(e.target.value) })}
              className="w-full bg-gray-950 border border-gray-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">Submit Code Rate Limit (Seconds)</label>
            <input
              type="number"
              value={settings.submit_code_rate_limit_sec}
              onChange={(e) => setSettings({ ...settings, submit_code_rate_limit_sec: Number(e.target.value) })}
              className="w-full bg-gray-950 border border-gray-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        {/* Toggles */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <label className="flex items-center justify-between p-4 bg-gray-950 border border-gray-800 rounded-2xl cursor-pointer">
            <span className="text-xs font-bold text-gray-300">Public Leaderboard Visible</span>
            <input
              type="checkbox"
              checked={settings.leaderboard_visible}
              onChange={(e) => setSettings({ ...settings, leaderboard_visible: e.target.checked })}
              className="w-5 h-5 accent-purple-600 rounded"
            />
          </label>

          <label className="flex items-center justify-between p-4 bg-gray-950 border border-gray-800 rounded-2xl cursor-pointer">
            <span className="text-xs font-bold text-gray-300">Freeze Leaderboard Updates</span>
            <input
              type="checkbox"
              checked={settings.leaderboard_frozen}
              onChange={(e) => setSettings({ ...settings, leaderboard_frozen: e.target.checked })}
              className="w-5 h-5 accent-purple-600 rounded"
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full py-3.5 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-xl transition-colors shadow-lg shadow-purple-600/30 flex items-center justify-center gap-2 text-sm disabled:opacity-50"
        >
          <Save className="w-4 h-4" /> Save Contest Settings
        </button>
      </form>
    </div>
  );
}
