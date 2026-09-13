"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { fetchApi } from '@/lib/api';
import Timer from '@/components/Timer';
import QuestionPalette from '@/components/QuestionPalette';
import AntiCheatNotifier from '@/components/AntiCheatNotifier';
import { CheckCircle2, Bookmark, ArrowLeft, ArrowRight, Send, AlertTriangle } from 'lucide-react';

interface QuestionItem {
  id: number;
  title: string;
  description: string;
  code_snippet?: string;
  category?: string;
  marks: number;
  negative_marks: number;
  options: { id: number; option_key: string; option_text: string }[];
}

export default function Round1Page() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [remainingSeconds, setRemainingSeconds] = useState<number>(1200);
  const [isSubmitted, setIsSubmitted] = useState(false);

  // Question answers: qId -> { selected_option, is_marked_for_review }
  const [answers, setAnswers] = useState<Record<number, { selected_option: string | null; is_marked_for_review: boolean }>>({});
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitModalOpen, setSubmitModalOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
      return;
    }
    if (user) {
      initRound1();
    }
  }, [user, isLoading, router]);

  const initRound1 = async () => {
    try {
      // 1. Start or fetch attempt
      const attemptData = await fetchApi('/rounds/1/start', { method: 'POST' });
      setRemainingSeconds(attemptData.remaining_seconds);
      setIsSubmitted(attemptData.is_submitted);

      if (attemptData.is_submitted) {
        router.push('/dashboard');
        return;
      }

      // 2. Fetch questions
      const qData = await fetchApi('/quiz/1/questions');
      setQuestions(qData);

      // 3. Restore state (saved answers)
      const stateData = await fetchApi('/quiz/1/state');
      const ansMap: Record<number, { selected_option: string | null; is_marked_for_review: boolean }> = {};
      
      qData.forEach((q: QuestionItem) => {
        ansMap[q.id] = { selected_option: null, is_marked_for_review: false };
      });

      if (stateData.answers) {
        stateData.answers.forEach((ans: any) => {
          ansMap[ans.question_id] = {
            selected_option: ans.selected_option,
            is_marked_for_review: ans.is_marked_for_review,
          };
        });
      }
      setAnswers(ansMap);

    } catch (err: any) {
      setError(err.message || 'Failed to initialize Round 1.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (optKey: string) => {
    if (isSubmitted) return;
    const currentQ = questions[currentIndex];
    const prev = answers[currentQ.id] || { selected_option: null, is_marked_for_review: false };

    const newAns = {
      ...prev,
      selected_option: prev.selected_option === optKey ? null : optKey,
    };

    setAnswers({ ...answers, [currentQ.id]: newAns });
    saveAnswerIncremental(currentQ.id, newAns.selected_option, newAns.is_marked_for_review);
  };

  const handleToggleMarkReview = () => {
    if (isSubmitted) return;
    const currentQ = questions[currentIndex];
    const prev = answers[currentQ.id] || { selected_option: null, is_marked_for_review: false };

    const newAns = {
      ...prev,
      is_marked_for_review: !prev.is_marked_for_review,
    };

    setAnswers({ ...answers, [currentQ.id]: newAns });
    saveAnswerIncremental(currentQ.id, newAns.selected_option, newAns.is_marked_for_review);
  };

  const saveAnswerIncremental = async (qId: number, selected: string | null, marked: boolean) => {
    try {
      await fetchApi('/quiz/1/answer', {
        method: 'POST',
        body: JSON.stringify({
          question_id: qId,
          selected_option: selected,
          is_marked_for_review: marked,
        }),
      });
    } catch (e) {
      console.error('Incremental answer save failed:', e);
    }
  };

  const handleSubmitRound1 = async () => {
    try {
      await fetchApi('/quiz/1/submit', { method: 'POST' });
      setIsSubmitted(true);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to submit Round 1.');
    }
  };

  if (isLoading || loading) {
    return <div className="py-20 text-center text-gray-400 font-mono animate-pulse">Initializing Round 1...</div>;
  }

  if (error) {
    return (
      <div className="max-w-xl mx-auto my-12 bg-red-950/80 border border-red-800 rounded-3xl p-6 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">Round 1 Error</h2>
        <p className="text-sm text-red-300">{error}</p>
        <button onClick={() => router.push('/dashboard')} className="px-6 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-xl font-semibold">
          Return to Dashboard
        </button>
      </div>
    );
  }

  const currentQ = questions[currentIndex];
  const currentAns = answers[currentQ?.id] || { selected_option: null, is_marked_for_review: false };

  return (
    <div className="space-y-6 py-2">
      <AntiCheatNotifier />

      {/* Header Bar */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl">
        <div>
          <span className="text-xs font-mono font-bold text-blue-400 uppercase tracking-wider">Round 1 — Coding Aptitude</span>
          <h1 className="text-xl font-extrabold text-white">Question {currentIndex + 1} of {questions.length}</h1>
        </div>

        <div className="flex items-center gap-4">
          <Timer initialSeconds={remainingSeconds} onExpire={handleSubmitRound1} />
          <button
            onClick={() => setSubmitModalOpen(true)}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/30 flex items-center gap-2 text-sm"
          >
            <Send className="w-4 h-4" /> Submit Round 1
          </button>
        </div>
      </div>

      {/* Main Grid Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Question Area */}
        <div className="lg:col-span-3 bg-gray-900 border border-gray-800 rounded-3xl p-6 sm:p-8 flex flex-col justify-between shadow-2xl space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded-md bg-gray-800 text-blue-400">
                {currentQ?.category || "Aptitude"}
              </span>
              <span className="text-xs font-mono text-gray-400">
                Marks: <strong className="text-emerald-400">+{currentQ?.marks}</strong> | Neg: <strong className="text-red-400">-{currentQ?.negative_marks}</strong>
              </span>
            </div>

            <h2 className="text-lg sm:text-xl font-bold text-white leading-relaxed">{currentQ?.description}</h2>

            {currentQ?.code_snippet && (
              <pre className="bg-[#0d1117] border border-gray-800 rounded-xl p-4 text-xs font-mono text-blue-300 overflow-x-auto">
                <code>{currentQ.code_snippet}</code>
              </pre>
            )}

            {/* Options */}
            <div className="space-y-3 pt-2">
              {currentQ?.options.map((opt) => {
                const isSelected = currentAns.selected_option === opt.option_key;
                return (
                  <button
                    key={opt.id}
                    onClick={() => handleSelectOption(opt.option_key)}
                    className={`w-full p-4 rounded-xl border text-left font-sans text-sm transition-all flex items-start gap-3 ${
                      isSelected
                        ? 'bg-blue-950/80 border-blue-500 text-white font-semibold shadow-lg shadow-blue-500/10'
                        : 'bg-gray-950 border-gray-800 text-gray-300 hover:border-gray-700 hover:bg-gray-900'
                    }`}
                  >
                    <span className={`w-6 h-6 rounded-lg font-mono text-xs font-bold flex items-center justify-center shrink-0 ${
                      isSelected ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400'
                    }`}>
                      {opt.option_key}
                    </span>
                    <span className="pt-0.5">{opt.option_text}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Action Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-gray-800">
            <button
              onClick={handleToggleMarkReview}
              className={`px-4 py-2.5 rounded-xl border text-xs font-bold flex items-center gap-2 transition-colors ${
                currentAns.is_marked_for_review
                  ? 'bg-purple-950 border-purple-600 text-purple-300'
                  : 'bg-gray-800 border-gray-700 text-gray-400 hover:text-white'
              }`}
            >
              <Bookmark className="w-4 h-4" />
              {currentAns.is_marked_for_review ? 'Marked for Review' : 'Mark for Review'}
            </button>

            <div className="flex items-center gap-3">
              <button
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
                className="px-4 py-2.5 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 text-white font-semibold rounded-xl text-xs flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" /> Previous
              </button>
              <button
                disabled={currentIndex === questions.length - 1}
                onClick={() => setCurrentIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white font-semibold rounded-xl text-xs flex items-center gap-2 shadow-md"
              >
                Next <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Palette Navigator */}
        <div className="lg:col-span-1">
          <QuestionPalette
            totalQuestions={questions.length}
            currentIndex={currentIndex}
            answers={answers}
            onSelect={(idx) => setCurrentIndex(idx)}
          />
        </div>
      </div>

      {/* Confirmation Modal */}
      {submitModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-800 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-xl font-bold text-white">Confirm Round 1 Submission</h3>
            <p className="text-sm text-gray-300 leading-relaxed">
              Are you sure you want to submit Round 1? Answers cannot be modified once submitted.
            </p>
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => setSubmitModalOpen(false)}
                className="w-1/2 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold rounded-xl text-sm"
              >
                Continue Quiz
              </button>
              <button
                onClick={handleSubmitRound1}
                className="w-1/2 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-sm shadow-lg shadow-emerald-600/30"
              >
                Confirm Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
