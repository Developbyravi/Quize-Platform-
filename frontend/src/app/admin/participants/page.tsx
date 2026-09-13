"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { fetchApi } from '@/lib/api';
import { Search, ShieldAlert, KeyRound, CheckCircle2, UserX } from 'lucide-react';

interface ParticipantItem {
  id: number;
  user_id: number;
  full_name: string;
  email: string;
  mobile_number: string;
  college_name: string;
  department: string;
  year: string;
  prn_student_id: string;
  is_disqualified: boolean;
  disqualification_reason?: string;
  violations_count: number;
}

export default function AdminParticipantsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [participants, setParticipants] = useState<ParticipantItem[]>([]);
  const [search, setSearch] = useState('');
  const [disqualifiedOnly, setDisqualifiedOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && (!user || user.role !== 'admin')) {
      router.push('/admin/login');
      return;
    }
    if (user && user.role === 'admin') {
      loadParticipants();
    }
  }, [user, isLoading, search, disqualifiedOnly, router]);

  const loadParticipants = async () => {
    try {
      const query = `/admin/participants?search=${encodeURIComponent(search)}&disqualified_only=${disqualifiedOnly}`;
      const data = await fetchApi(query);
      setParticipants(data);
    } catch (e) {
      console.error('Failed to fetch participants:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleDisqualify = async (id: number) => {
    try {
      await fetchApi(`/admin/participants/${id}/disqualify`, { method: 'POST' });
      loadParticipants();
    } catch (e) {
      console.error('Disqualify failed:', e);
    }
  };

  const handleResetPassword = async (id: number) => {
    try {
      const res = await fetchApi(`/admin/participants/${id}/reset-password`, { method: 'POST' });
      alert(res.message);
    } catch (e) {
      console.error('Password reset failed:', e);
    }
  };

  if (isLoading || loading) {
    return <div className="py-20 text-center text-purple-400 font-mono animate-pulse">Loading Participant Roster...</div>;
  }

  return (
    <div className="space-y-6 py-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white">Participant Management</h1>
          <p className="text-sm text-gray-400 mt-1">Inspect roster, manage disqualifications, and reset passwords.</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search name, PRN, email..."
              className="bg-gray-900 border border-gray-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-purple-500"
            />
          </div>
          <button
            onClick={() => setDisqualifiedOnly(!disqualifiedOnly)}
            className={`px-3 py-2 rounded-xl border text-xs font-semibold ${
              disqualifiedOnly ? 'bg-red-950 border-red-800 text-red-300' : 'bg-gray-900 border-gray-800 text-gray-400'
            }`}
          >
            Disqualified Only
          </button>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-300">
            <thead className="bg-[#161b22] text-xs font-mono text-gray-400 uppercase border-b border-gray-800">
              <tr>
                <th className="px-6 py-4">Name / PRN</th>
                <th className="px-6 py-4">Email / Mobile</th>
                <th className="px-6 py-4">College / Dept</th>
                <th className="px-4 py-4 text-center">Violations</th>
                <th className="px-4 py-4 text-center">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {participants.map((p) => (
                <tr key={p.id} className="hover:bg-gray-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-bold text-white">{p.full_name}</div>
                    <div className="text-xs font-mono text-purple-400">{p.prn_student_id}</div>
                  </td>
                  <td className="px-6 py-4 text-xs font-mono">
                    <div className="text-gray-300">{p.email}</div>
                    <div className="text-gray-500">{p.mobile_number}</div>
                  </td>
                  <td className="px-6 py-4 text-xs">
                    <div className="text-gray-300">{p.college_name}</div>
                    <div className="text-gray-500 font-mono">{p.department} ({p.year})</div>
                  </td>
                  <td className="px-4 py-4 text-center font-mono font-bold">
                    <span className={p.violations_count > 0 ? "text-amber-400" : "text-gray-500"}>
                      {p.violations_count}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-center font-mono text-xs">
                    {p.is_disqualified ? (
                      <span className="px-2.5 py-1 rounded-full bg-red-950 text-red-400 border border-red-800 font-bold">
                        DISQUALIFIED
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">
                        ACTIVE
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button
                      onClick={() => handleToggleDisqualify(p.id)}
                      className={`px-3 py-1.5 rounded-lg border text-xs font-bold ${
                        p.is_disqualified
                          ? 'bg-emerald-950 border-emerald-800 text-emerald-400 hover:bg-emerald-900'
                          : 'bg-red-950 border-red-800 text-red-400 hover:bg-red-900'
                      }`}
                    >
                      {p.is_disqualified ? 'Restore' : 'Disqualify'}
                    </button>
                    <button
                      onClick={() => handleResetPassword(p.id)}
                      className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 rounded-lg text-xs font-semibold"
                    >
                      Reset PW
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
