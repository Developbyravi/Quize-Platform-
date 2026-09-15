"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { fetchApi } from '@/lib/api';
import Timer from '@/components/Timer';
import CodeEditor from '@/components/CodeEditor';
import AntiCheatNotifier from '@/components/AntiCheatNotifier';
import { Play, Send, AlertTriangle, Trophy, Terminal as ConsoleIcon, Code2 } from 'lucide-react';

interface QuestionItem {
  id: number;
  title: string;
  description: string;
  difficulty?: string;
  marks: number;
  language: string;
  input_format?: string;
  output_format?: string;
  constraints?: string;
  sample_input?: string;
  sample_output?: string;
}

interface RunResult {
  status: string;
  score?: number;
  passed_test_cases?: number;
  total_test_cases?: number;
  execution_time_ms?: number;
  memory_kb?: number;
  stdout?: string;
  stderr?: string;
  compile_output?: string;
  error_message?: string;
}

export default function Round3Page() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [editorCode, setEditorCode] = useState('def solve():\n    pass\n');
  const [editorLang, setEditorLang] = useState('python');
  const [remainingSeconds, setRemainingSeconds] = useState(2100);
  
  const [consoleResult, setConsoleResult] = useState<RunResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
      return;
    }
    if (user?.role === 'admin') {
      setError('You are currently logged in as an Administrator. Administrator accounts cannot participate in competition rounds. Please log in with a Participant account.');
      setLoading(false);
      return;
    }
    if (user) {
      initRound3();
    }
  }, [user, isLoading, router]);

  const initRound3 = async () => {
    try {
      const attemptData = await fetchApi('/rounds/3/start', { method: 'POST' });
      setRemainingSeconds(attemptData.remaining_seconds);

      if (attemptData.is_submitted) {
        router.push('/dashboard');
        return;
      }

      // Fetch Round 3 questions (2 Coding Problems)
      const qData = await fetchApi('/quiz/3/questions');
      setQuestions(qData);

      if (qData.length > 0) {
        loadQuestionCode(qData[0]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to initialize Round 3.');
    } finally {
      setLoading(false);
    }
  };

  const loadQuestionCode = async (q: QuestionItem) => {
    try {
      const draft = await fetchApi(`/code/draft/${q.id}`).catch(() => null);
      if (draft && draft.code) {
        setEditorCode(draft.code);
        setEditorLang(draft.language || q.language || 'python');
      } else {
        setEditorCode('# Write your solution here\nimport sys\n');
        setEditorLang(q.language || 'python');
      }
    } catch {
      setEditorCode('# Write your solution here\nimport sys\n');
      setEditorLang(q.language || 'python');
    }
  };

  const handleSelectQuestion = (index: number) => {
    setCurrentQIndex(index);
    setConsoleResult(null);
    if (questions[index]) {
      loadQuestionCode(questions[index]);
    }
  };

  const handleAutosave = async (codeToSave: string) => {
    const currentQ = questions[currentQIndex];
    if (!currentQ) return;
    try {
      await fetchApi('/code/autosave', {
        method: 'POST',
        body: JSON.stringify({
          question_id: currentQ.id,
          round_id: 3,
          code: codeToSave,
          language: editorLang,
        }),
      });
    } catch (e) {
      console.error('Autosave failed:', e);
    }
  };

  const handleRunCode = async () => {
    const currentQ = questions[currentQIndex];
    if (!currentQ) return;
    setIsExecuting(true);
    setConsoleResult(null);

    handleAutosave(editorCode);

    try {
      const res = await fetchApi('/code/run', {
        method: 'POST',
        body: JSON.stringify({
          question_id: currentQ.id,
          round_id: 3,
          source_code: editorCode,
          language: editorLang,
        }),
      });
      setConsoleResult(res);
    } catch (err: any) {
      setConsoleResult({
        status: 'ERROR',
        error_message: err.message || 'Execution request failed.',
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleSubmitCode = async () => {
    const currentQ = questions[currentQIndex];
    if (!currentQ) return;
    setIsExecuting(true);
    setConsoleResult(null);

    handleAutosave(editorCode);

    try {
      const res = await fetchApi('/code/submit', {
        method: 'POST',
        body: JSON.stringify({
          question_id: currentQ.id,
          round_id: 3,
          source_code: editorCode,
          language: editorLang,
        }),
      });
      setConsoleResult(res);
    } catch (err: any) {
      setConsoleResult({
        status: 'ERROR',
        error_message: err.message || 'Submission request failed.',
      });
    } finally {
      setIsExecuting(false);
    }
  };

  if (isLoading || loading) {
    return <div className="py-20 text-center text-gray-400 font-mono animate-pulse">Initializing Round 3 Coding Arena...</div>;
  }

  if (error) {
    return (
      <div className="max-w-xl mx-auto my-12 bg-red-950/80 border border-red-800 rounded-3xl p-6 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">Round 3 Error</h2>
        <p className="text-sm text-red-300">{error}</p>
        <button onClick={() => router.push('/dashboard')} className="px-6 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-xl font-semibold">
          Return to Dashboard
        </button>
      </div>
    );
  }

  const currentQ = questions[currentQIndex];

  return (
    <div className="space-y-4 py-2">
      <AntiCheatNotifier roundId={3} />

      {/* Header Bar */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-800 text-emerald-400 flex items-center justify-center font-bold">
            <Trophy className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">Round 3 — Final Coding Challenge</span>
            <h1 className="text-xl font-extrabold text-white">Problem {currentQIndex + 1} of {questions.length}</h1>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Timer initialSeconds={remainingSeconds} />
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold rounded-xl text-xs"
          >
            Dashboard
          </button>
        </div>
      </div>

      {/* Problem Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {questions.map((q, idx) => (
          <button
            key={q.id}
            onClick={() => handleSelectQuestion(idx)}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center gap-2 ${
              idx === currentQIndex
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30'
                : 'bg-gray-900 text-gray-400 hover:bg-gray-800 hover:text-white border border-gray-800'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" /> Problem {idx + 1} ({q.marks} Marks)
          </button>
        ))}
      </div>

      {/* Main Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[720px]">
        
        {/* Left Sidebar: Problem Specification */}
        <div className="lg:col-span-5 bg-gray-900 border border-gray-800 rounded-2xl p-5 flex flex-col justify-between overflow-y-auto space-y-4 shadow-xl">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <span className="text-xs font-mono font-bold text-emerald-400 uppercase">{currentQ?.title || "Algorithmic Challenge"}</span>
              <span className="text-xs font-mono text-emerald-400 font-bold">+{currentQ?.marks || 50} Marks</span>
            </div>

            <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">{currentQ?.description}</p>

            {currentQ?.input_format && (
              <div className="space-y-1 text-xs font-mono">
                <span className="text-gray-400 font-semibold uppercase">Input Format</span>
                <p className="text-gray-300 whitespace-pre-line bg-gray-950 p-2.5 rounded-lg border border-gray-800">{currentQ.input_format}</p>
              </div>
            )}

            {currentQ?.output_format && (
              <div className="space-y-1 text-xs font-mono">
                <span className="text-gray-400 font-semibold uppercase">Output Format</span>
                <p className="text-gray-300 whitespace-pre-line bg-gray-950 p-2.5 rounded-lg border border-gray-800">{currentQ.output_format}</p>
              </div>
            )}

            {currentQ?.constraints && (
              <div className="space-y-1 text-xs font-mono">
                <span className="text-gray-400 font-semibold uppercase">Constraints</span>
                <p className="text-amber-300 whitespace-pre-line bg-gray-950 p-2.5 rounded-lg border border-gray-800">{currentQ.constraints}</p>
              </div>
            )}

            {currentQ?.sample_input && (
              <div className="space-y-1 text-xs font-mono">
                <span className="text-gray-400 font-semibold uppercase">Sample Input</span>
                <pre className="bg-[#0d1117] border border-gray-800 rounded-lg p-3 text-blue-300 overflow-x-auto">{currentQ.sample_input}</pre>
              </div>
            )}

            {currentQ?.sample_output && (
              <div className="space-y-1 text-xs font-mono">
                <span className="text-gray-400 font-semibold uppercase">Sample Output</span>
                <pre className="bg-[#0d1117] border border-gray-800 rounded-lg p-3 text-emerald-300 overflow-x-auto">{currentQ.sample_output}</pre>
              </div>
            )}
          </div>
        </div>

        {/* Right Pane: Monaco Editor + Console */}
        <div className="lg:col-span-7 flex flex-col gap-4 h-full">
          
          {/* Monaco Code Editor */}
          <div className="flex-1 min-h-[420px]">
            <CodeEditor
              code={editorCode}
              onChange={(val) => setEditorCode(val)}
              language={editorLang}
              onLanguageChange={(lang) => setEditorLang(lang)}
              onAutosave={handleAutosave}
            />
          </div>

          {/* Controls & Console Panel */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-4 space-y-3 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-mono font-bold text-gray-400">
                <ConsoleIcon className="w-4 h-4 text-emerald-400" /> Console & Test Case Results
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleRunCode}
                  disabled={isExecuting}
                  className="px-5 py-2 bg-gray-800 hover:bg-gray-700 text-blue-400 font-bold rounded-xl border border-gray-700 transition-colors text-xs flex items-center gap-1.5 disabled:opacity-50"
                >
                  <Play className="w-3.5 h-3.5 fill-blue-400" /> Run Code
                </button>
                <button
                  onClick={handleSubmitCode}
                  disabled={isExecuting}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/30 transition-colors text-xs flex items-center gap-1.5 disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" /> Submit Code
                </button>
              </div>
            </div>

            {/* Console Output Display */}
            <div className="bg-[#0d1117] border border-gray-800 rounded-xl p-3 text-xs font-mono min-h-[100px] max-h-[140px] overflow-y-auto">
              {isExecuting ? (
                <span className="text-emerald-400 animate-pulse">Evaluating solution via Judge0 execution engine...</span>
              ) : consoleResult ? (
                <div className="space-y-1">
                  <div className="flex items-center justify-between border-b border-gray-800 pb-1 mb-2">
                    <span className={`font-bold ${consoleResult.status === 'ACCEPTED' ? 'text-emerald-400' : 'text-amber-400'}`}>
                      Status: {consoleResult.status} {consoleResult.passed_test_cases !== undefined && `(${consoleResult.passed_test_cases}/${consoleResult.total_test_cases} Test Cases Passed)`}
                    </span>
                    {consoleResult.score !== undefined && (
                      <span className="text-emerald-400 font-bold">Awarded Score: {consoleResult.score} Marks</span>
                    )}
                  </div>

                  {consoleResult.error_message && (
                    <div className="text-red-400">{consoleResult.error_message}</div>
                  )}
                  {consoleResult.compile_output && (
                    <div className="text-red-400">Compile Output: {consoleResult.compile_output}</div>
                  )}
                  {consoleResult.stdout && (
                    <div className="text-gray-200">Output: {consoleResult.stdout}</div>
                  )}
                  {consoleResult.stderr && (
                    <div className="text-amber-400">Errors: {consoleResult.stderr}</div>
                  )}
                </div>
              ) : (
                <span className="text-gray-600">Click "Run Code" or "Submit Code" to evaluate your solution.</span>
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
