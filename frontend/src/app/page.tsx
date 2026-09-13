import Link from 'next/link';
import { Terminal, ShieldAlert, Cpu, Trophy, Code2, ArrowRight, CheckCircle, HelpCircle, Flame } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="space-y-16 py-6">
      
      {/* HERO SECTION */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-gray-900 via-[#0d1322] to-[#090d16] border border-gray-800 p-8 sm:p-14 text-center shadow-2xl">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-600/10 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-950/80 border border-blue-800 text-blue-400 text-xs font-mono font-semibold mb-6">
          <Flame className="w-4 h-4 text-amber-400" /> Engineering Day 2026 Official Contest
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight max-w-4xl mx-auto">
          Think. Code. Debug. <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">Win.</span>
        </h1>

        <p className="mt-4 text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
          Welcome to the annual college <strong className="text-gray-200">Engineering Day Coding Challenge</strong>. Compete across 3 high-stakes rounds designed to test your core aptitude, debugging prowess, and algorithmic code speed.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link
            href="/register"
            className="px-8 py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-600/30 flex items-center gap-2 text-base"
          >
            Register Now <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            href="/login"
            className="px-8 py-3.5 bg-gray-800 hover:bg-gray-700 text-gray-200 font-bold rounded-xl border border-gray-700 transition-all text-base"
          >
            Participant Login
          </Link>
          <Link
            href="/rules"
            className="px-8 py-3.5 bg-gray-900/80 hover:bg-gray-800 text-gray-400 hover:text-white font-semibold rounded-xl border border-gray-800 transition-all text-base"
          >
            Competition Rules
          </Link>
        </div>
      </section>

      {/* 3 CONTEST ROUNDS */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-extrabold text-white">3 Competition Rounds</h2>
          <p className="text-gray-400">Every round brings unique technical challenges and rigorous automated evaluation.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Round 1 */}
          <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 hover:border-blue-500/50 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-blue-950 border border-blue-800 text-blue-400 flex items-center justify-center font-bold text-lg mb-4 group-hover:scale-110 transition-transform">
              R1
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Coding Aptitude</h3>
            <p className="text-sm text-gray-400 mb-4 leading-relaxed">
              20 Multiple Choice Questions testing DSA concepts, C/C++, Java, Python syntax, OOP, time complexity, and output prediction.
            </p>
            <ul className="space-y-2 text-xs text-gray-400 font-mono">
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-400" /> Duration: 20 Minutes</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-400" /> 20 Questions (MCQ)</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-amber-400" /> Optional Negative Marking</li>
            </ul>
          </div>

          {/* Round 2 */}
          <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 hover:border-purple-500/50 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-purple-950 border border-purple-800 text-purple-400 flex items-center justify-center font-bold text-lg mb-4 group-hover:scale-110 transition-transform">
              R2
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Debug the Code</h3>
            <p className="text-sm text-gray-400 mb-4 leading-relaxed">
              5–8 Debugging challenges with buggy code snippets. Identify off-by-one errors, memory leaks, and logic flaws in Monaco Editor.
            </p>
            <ul className="space-y-2 text-xs text-gray-400 font-mono">
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-400" /> Duration: 35 Minutes</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-400" /> Monaco Editor Integration</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-blue-400" /> Judge0 Execution Engine</li>
            </ul>
          </div>

          {/* Round 3 */}
          <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 hover:border-emerald-500/50 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-emerald-950 border border-emerald-800 text-emerald-400 flex items-center justify-center font-bold text-lg mb-4 group-hover:scale-110 transition-transform">
              R3
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Final Coding Challenge</h3>
            <p className="text-sm text-gray-400 mb-4 leading-relaxed">
              3 Algorithmic problems (Easy $\rightarrow$ Medium $\rightarrow$ Hard). Implement optimal solutions and pass hidden test cases for partial scoring.
            </p>
            <ul className="space-y-2 text-xs text-gray-400 font-mono">
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-400" /> Duration: 60 Minutes</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-400" /> Partial Scoring by Test Cases</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-purple-400" /> Hidden Test Case Protection</li>
            </ul>
          </div>
        </div>
      </section>

      {/* SUPPORTED LANGUAGES */}
      <section className="bg-gray-900/40 border border-gray-800 rounded-2xl p-8">
        <h2 className="text-2xl font-bold text-white text-center mb-6">Supported Programming Languages</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto">
          {["C (GCC 11)", "C++ (GCC 14)", "Java (OpenJDK 13)", "Python 3.8+"].map((lang) => (
            <div key={lang} className="bg-gray-900 border border-gray-700/80 rounded-xl p-4 text-center font-mono font-semibold text-blue-400 shadow-md">
              {lang}
            </div>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-white text-center">Frequently Asked Questions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-5">
            <h4 className="font-bold text-white mb-1 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-blue-400" /> Can I change my code draft if I refresh?
            </h4>
            <p className="text-sm text-gray-400">
              Yes! Monaco editor code autosaves every 15 seconds. Browser refreshes, crashes, or drops automatically restore your exact code draft and server timer.
            </p>
          </div>

          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-5">
            <h4 className="font-bold text-white mb-1 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-blue-400" /> How are ties broken on the leaderboard?
            </h4>
            <p className="text-sm text-gray-400">
              Ties are broken automatically: (1) Highest total score, (2) Lowest total contest submission time, (3) Earliest final accepted submission.
            </p>
          </div>
        </div>
      </section>

    </div>
  );
}
