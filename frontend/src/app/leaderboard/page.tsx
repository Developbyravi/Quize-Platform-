"use client";

import { useEffect, useState } from 'react';
import { fetchApi } from '@/lib/api';
import { Trophy, Medal, Clock, ShieldAlert, Award, Search, EyeOff } from 'lucide-react';

interface Entry {
  rank: number;
  participant_id: number;
  full_name: string;
  college_name: string;
  department: string;
  round1_score: number;
  round2_score: number;
  round3_score: number;
  total_score: number;
  total_time_sec: number;
  is_disqualified: boolean;
}

export default function LeaderboardPage() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [isVisible, setIsVisible] = useState(true);
  const [isFrozen, setIsFrozen] = useState(false);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      const data = await fetchApi('/leaderboard');
      setIsVisible(data.is_visible);
      setIsFrozen(data.is_frozen);
      setEntries(data.entries || []);
    } catch (e) {
      console.error('Failed to load leaderboard:', e);
    } finally {
      setLoading(false);
    }
  };

  const filtered = entries.filter(
    (e) =>
      e.full_name.toLowerCase().includes(search.toLowerCase()) ||
      e.college_name.toLowerCase().includes(search.toLowerCase()) ||
      e.department.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return <div className="py-20 text-center text-gray-400 font-mono animate-pulse">Loading competition standings...</div>;
  }

  if (!isVisible) {
    return (
      <div className="max-w-xl mx-auto my-16 bg-gray-900 border border-gray-800 rounded-3xl p-8 text-center space-y-4 shadow-2xl">
        <EyeOff className="w-12 h-12 text-amber-400 mx-auto" />
        <h1 className="text-2xl font-extrabold text-white">Leaderboard Standings Hidden</h1>
        <p className="text-sm text-gray-400 leading-relaxed">
          The contest administrator has temporarily hidden the live leaderboard. Standings will be published at the conclusion of the event.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8 py-4">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-amber-950/40 via-gray-900 to-indigo-950/40 border border-amber-800/40 rounded-3xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-2xl">
        <div>
          <span className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider">Engineering Day 2026</span>
          <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
            <Trophy className="w-8 h-8 text-amber-400" /> Contest Standings
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Tie-breaking Order: (1) Total Score DESC $\rightarrow$ (2) Total Time ASC $\rightarrow$ (3) Earliest Final Submission ASC.
          </p>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search participant..."
            className="w-full bg-gray-950 border border-gray-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-amber-500"
          />
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-300">
            <thead className="bg-[#161b22] text-xs font-mono text-gray-400 uppercase border-b border-gray-800">
              <tr>
                <th className="px-6 py-4">Rank</th>
                <th className="px-6 py-4">Participant</th>
                <th className="px-6 py-4">College / Dept</th>
                <th className="px-4 py-4 text-center">Round 1</th>
                <th className="px-4 py-4 text-center">Round 2</th>
                <th className="px-4 py-4 text-center">Round 3</th>
                <th className="px-6 py-4 text-right">Total Score</th>
                <th className="px-6 py-4 text-right">Total Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {filtered.map((e) => {
                let rankIcon = null;
                let rankBadgeClass = "text-gray-400 font-mono";

                if (e.rank === 1) {
                  rankIcon = <span className="text-xl">🏆</span>;
                  rankBadgeClass = "text-amber-400 font-bold font-mono text-base";
                } else if (e.rank === 2) {
                  rankIcon = <span className="text-xl">🥈</span>;
                  rankBadgeClass = "text-gray-300 font-bold font-mono text-base";
                } else if (e.rank === 3) {
                  rankIcon = <span className="text-xl">🥉</span>;
                  rankBadgeClass = "text-amber-600 font-bold font-mono text-base";
                }

                return (
                  <tr
                    key={e.participant_id}
                    className={`hover:bg-gray-800/50 transition-colors ${
                      e.is_disqualified ? 'bg-red-950/20 text-red-400 line-through opacity-60' : ''
                    }`}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {rankIcon}
                        <span className={rankBadgeClass}>#{e.rank}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-bold text-white">{e.full_name}</div>
                      {e.is_disqualified && (
                        <span className="text-xs text-red-500 font-mono uppercase font-bold">Disqualified</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-xs text-gray-300">{e.college_name}</div>
                      <div className="text-xs text-gray-500 font-mono">{e.department}</div>
                    </td>
                    <td className="px-4 py-4 text-center font-mono text-blue-400">{e.round1_score}</td>
                    <td className="px-4 py-4 text-center font-mono text-purple-400">{e.round2_score}</td>
                    <td className="px-4 py-4 text-center font-mono text-emerald-400">{e.round3_score}</td>
                    <td className="px-6 py-4 text-right font-mono font-extrabold text-amber-400 text-base">
                      {e.total_score}
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-xs text-gray-400">
                      {Math.round(e.total_time_sec)}s
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
