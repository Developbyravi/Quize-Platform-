"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { fetchApi } from '@/lib/api';
import { FileCode, Code, CheckCircle2, XCircle, AlertCircle, Clock } from 'lucide-react';

interface SubmissionItem {
  id: number;
  participant_name: string;
  question_id: number;
  round_id: number;
  language: string;
  status: string;
  score: number;
  passed_test_cases: number;
  total_test_cases: number;
  execution_time_ms?: number;
  memory_kb?: number;
  source_code: string;
  submitted_at: string;
}

export default function AdminSubmissionsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [submissions, setSubmissions] = useState<SubmissionItem[]>([]);
  const [selectedSub, setSelectedSub] = useState<SubmissionItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && (!user || user.role !== 'admin')) {
      router.push('/admin/login');
      return;
    }
    if (user && user.role === 'admin') {
      loadSubmissions();
    }
  }, [user, isLoading, router]);

  const loadSubmissions = async () => {
    try {
      const data = await fetchApi('/admin/submissions');
      setSubmissions(data);
    } catch (e) {
      console.error('Failed to fetch submissions:', e);
    } finally {
      setLoading(false);
    }
  };

  if (isLoading || loading) {
    return <div className="py-20 text-center text-purple-400 font-mono animate-pulse">Loading Submissions Stream...</div>;
  }

  return (
    <div className="space-y-6 py-4">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-extrabold text-white">Submission Inspector</h1>
        <p className="text-sm text-gray-400 mt-1">Audit code submissions, test case ratios, execution time, and memory.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-300">
            <thead className="bg-[#161b22] text-xs font-mono text-gray-400 uppercase border-b border-gray-800">
              <tr>
                <th className="px-6 py-4">ID</th>
                <th className="px-6 py-4">Participant</th>
                <th className="px-4 py-4 text-center">Round / Question</th>
                <th className="px-4 py-4 text-center">Language</th>
                <th className="px-6 py-4 text-center">Status</th>
                <th className="px-4 py-4 text-center">Score</th>
                <th className="px-6 py-4 text-right">Execution</th>
                <th className="px-6 py-4 text-right">Inspect Code</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {submissions.map((s) => (
                <tr key={s.id} className="hover:bg-gray-800/50 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-gray-500">#{s.id}</td>
                  <td className="px-6 py-4 font-bold text-white">{s.participant_name}</td>
                  <td className="px-4 py-4 text-center font-mono text-xs text-purple-400">R{s.round_id} / Q{s.question_id}</td>
                  <td className="px-4 py-4 text-center font-mono text-xs text-blue-400 uppercase">{s.language}</td>
                  <td className="px-6 py-4 text-center font-mono text-xs">
                    <span className={`px-2.5 py-1 rounded-full font-bold border ${
                      s.status === 'ACCEPTED' ? 'bg-emerald-950 text-emerald-400 border-emerald-800' : 'bg-red-950 text-red-400 border-red-800'
                    }`}>
                      {s.status} ({s.passed_test_cases}/{s.total_test_cases})
                    </span>
                  </td>
                  <td className="px-4 py-4 text-center font-mono font-bold text-emerald-400">{s.score}</td>
                  <td className="px-6 py-4 text-right font-mono text-xs text-gray-400">
                    {s.execution_time_ms ? `${s.execution_time_ms} ms` : '-'}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => setSelectedSub(s)}
                      className="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-blue-400 border border-gray-700 rounded-lg text-xs font-semibold"
                    >
                      View Source
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Code Inspection Modal */}
      {selectedSub && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-800 rounded-3xl p-6 max-w-2xl w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <div>
                <h3 className="text-lg font-bold text-white">Submitted Source Code</h3>
                <span className="text-xs font-mono text-gray-400">Participant: {selectedSub.participant_name} | Language: {selectedSub.language}</span>
              </div>
              <button onClick={() => setSelectedSub(null)} className="text-gray-400 hover:text-white font-bold">
                ✕
              </button>
            </div>

            <pre className="bg-[#0d1117] border border-gray-800 rounded-2xl p-4 text-xs font-mono text-blue-300 max-h-96 overflow-y-auto">
              <code>{selectedSub.source_code}</code>
            </pre>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedSub(null)}
                className="px-5 py-2 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-xl text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
