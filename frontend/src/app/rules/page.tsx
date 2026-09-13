import { BookOpen, AlertTriangle, ShieldCheck, Clock, CheckCircle } from 'lucide-react';

export default function RulesPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-blue-500" /> Competition Rules & Guidelines
        </h1>
        <p className="text-gray-400 mt-1">Engineering Day 2026 — Official Coding Competition Code of Conduct</p>
      </div>

      <div className="space-y-6">
        {/* General Rules */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" /> 1. Individual Participation
          </h2>
          <p className="text-sm text-gray-300 leading-relaxed">
            Every student must register individually using their valid email, mobile number, and student PRN ID. Multiple registrations per participant are strictly forbidden.
          </p>
        </div>

        {/* 3 Rounds & Timing */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" /> 2. Contest Structure & Server Timers
          </h2>
          <ul className="space-y-2 text-sm text-gray-300 list-disc list-inside">
            <li><strong>Round 1 (Coding Aptitude):</strong> 20 Multiple Choice Questions (20 minutes). Answers cannot be edited after submission.</li>
            <li><strong>Round 2 (Debug the Code):</strong> 5 Debugging Challenges (35 minutes). Fix syntax/logic bugs in Monaco Editor.</li>
            <li><strong>Round 3 (Final Coding Challenge):</strong> 3 Algorithmic Problems (60 minutes). Partial scoring applies based on hidden test cases passed.</li>
            <li><strong>Server-Authoritative Timers:</strong> Timers are enforced strictly by server timestamps. When time expires, your round will automatically lock and submit.</li>
          </ul>
        </div>

        {/* Anti-Cheating Policy */}
        <div className="bg-red-950/30 border border-red-900/60 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-bold text-red-400 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" /> 3. Anti-Cheating & Disqualification Policy
          </h2>
          <p className="text-sm text-gray-300 leading-relaxed">
            The platform automatically monitors tab switching, window blur, and suspicious request frequencies.
          </p>
          <ul className="space-y-2 text-sm text-red-300 list-disc list-inside">
            <li>Switching tabs or leaving the competition window displays an immediate warning and logs a violation.</li>
            <li>Accumulating violations beyond the administrator-set limit will result in immediate account disqualification.</li>
            <li>Use of unauthorized external AI tools, communication apps, or proxy submissions is prohibited.</li>
          </ul>
        </div>

        {/* Scoring & Leaderboard */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-amber-400" /> 4. Scoring & Tie-Breaking Rules
          </h2>
          <p className="text-sm text-gray-300">
            Leaderboard standings are determined strictly by the following 3-tier tie-breaking algorithm:
          </p>
          <ol className="space-y-2 text-sm text-gray-300 list-decimal list-inside font-mono">
            <li>Highest Cumulative Score across all 3 rounds</li>
            <li>Lowest Cumulative Contest Time taken</li>
            <li>Earliest Final Accepted Submission Timestamp</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
