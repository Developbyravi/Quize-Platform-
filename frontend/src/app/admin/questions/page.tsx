"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { fetchApi } from '@/lib/api';
import { 
  FileCode, Plus, Edit3, Trash2, Copy, Eye, Search, Filter, 
  CheckCircle2, XCircle, AlertTriangle, Layers, Code, CheckSquare, 
  HelpCircle, RefreshCw, X 
} from 'lucide-react';

interface OptionItem {
  id?: number;
  option_key: string;
  option_text: string;
  is_correct: boolean;
}

interface TestCaseItem {
  id?: number;
  input_data: string;
  expected_output: string;
  is_hidden: boolean;
  weight: number;
}

interface QuestionItem {
  id: number;
  round_id: number;
  title: string;
  description: string;
  code_snippet?: string;
  category?: string;
  marks: number;
  negative_marks: number;
  difficulty: string;
  language: string;
  order_index: number;
  input_format?: string;
  output_format?: string;
  constraints?: string;
  sample_input?: string;
  sample_output?: string;
  options: OptionItem[];
  test_cases: TestCaseItem[];
}

const DEFAULT_OPTIONS: OptionItem[] = [
  { option_key: 'A', option_text: '', is_correct: true },
  { option_key: 'B', option_text: '', is_correct: false },
  { option_key: 'C', option_text: '', is_correct: false },
  { option_key: 'D', option_text: '', is_correct: false },
];

const DEFAULT_TEST_CASES: TestCaseItem[] = [
  { input_data: '1 2', expected_output: '3', is_hidden: false, weight: 1.0 },
  { input_data: '10 20', expected_output: '30', is_hidden: true, weight: 1.0 },
];

export default function AdminQuestionsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [selectedRound, setSelectedRound] = useState<number>(0); // 0 = All
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [loading, setLoading] = useState(true);

  // Modals state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  const [editingQuestion, setEditingQuestion] = useState<QuestionItem | null>(null);
  const [viewingQuestion, setViewingQuestion] = useState<QuestionItem | null>(null);
  const [deletingQuestion, setDeletingQuestion] = useState<QuestionItem | null>(null);

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    round_id: 1,
    title: '',
    description: '',
    code_snippet: '',
    category: 'DSA',
    marks: 5.0,
    negative_marks: 0.0,
    difficulty: 'Medium',
    language: 'python',
    order_index: 1,
    input_format: '',
    output_format: '',
    constraints: '',
    sample_input: '',
    sample_output: '',
    options: DEFAULT_OPTIONS,
    test_cases: DEFAULT_TEST_CASES,
  });

  useEffect(() => {
    if (!isLoading && (!user || user.role !== 'admin')) {
      router.push('/admin/login');
      return;
    }
    if (user && user.role === 'admin') {
      loadQuestions();
    }
  }, [user, isLoading, router]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const data = await fetchApi('/admin/questions');
      setQuestions(data);
    } catch (e: any) {
      setErrorMsg(e.message || 'Failed to load questions.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAdd = (roundId: number = 1) => {
    setEditingQuestion(null);
    setFormData({
      round_id: roundId,
      title: '',
      description: '',
      code_snippet: '',
      category: 'DSA',
      marks: roundId === 1 ? 5.0 : roundId === 2 ? 10.0 : 20.0,
      negative_marks: roundId === 1 ? 1.0 : 0.0,
      difficulty: 'Medium',
      language: 'python',
      order_index: questions.filter(q => q.round_id === roundId).length + 1,
      input_format: '',
      output_format: '',
      constraints: '',
      sample_input: '',
      sample_output: '',
      options: [
        { option_key: 'A', option_text: '', is_correct: true },
        { option_key: 'B', option_text: '', is_correct: false },
        { option_key: 'C', option_text: '', is_correct: false },
        { option_key: 'D', option_text: '', is_correct: false },
      ],
      test_cases: [
        { input_data: '', expected_output: '', is_hidden: false, weight: 1.0 },
        { input_data: '', expected_output: '', is_hidden: true, weight: 1.0 },
      ],
    });
    setErrorMsg(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (q: QuestionItem) => {
    setEditingQuestion(q);
    setFormData({
      round_id: q.round_id,
      title: q.title,
      description: q.description,
      code_snippet: q.code_snippet || '',
      category: q.category || 'DSA',
      marks: q.marks,
      negative_marks: q.negative_marks,
      difficulty: q.difficulty || 'Medium',
      language: q.language || 'python',
      order_index: q.order_index || 1,
      input_format: q.input_format || '',
      output_format: q.output_format || '',
      constraints: q.constraints || '',
      sample_input: q.sample_input || '',
      sample_output: q.sample_output || '',
      options: q.options && q.options.length > 0 ? q.options.map(o => ({
        option_key: o.option_key,
        option_text: o.option_text,
        is_correct: o.is_correct
      })) : DEFAULT_OPTIONS,
      test_cases: q.test_cases && q.test_cases.length > 0 ? q.test_cases.map(tc => ({
        input_data: tc.input_data,
        expected_output: tc.expected_output,
        is_hidden: tc.is_hidden,
        weight: tc.weight
      })) : DEFAULT_TEST_CASES,
    });
    setErrorMsg(null);
    setIsModalOpen(true);
  };

  const handleSaveQuestion = async () => {
    setErrorMsg(null);

    // Basic Validation
    if (!formData.title.trim()) {
      setErrorMsg('Question Title is required.');
      return;
    }
    if (!formData.description.trim()) {
      setErrorMsg('Question Description is required.');
      return;
    }

    if (formData.round_id === 1) {
      if (formData.options.some(o => !o.option_text.trim())) {
        setErrorMsg('All option texts must be filled for Round 1.');
        return;
      }
      const correctCount = formData.options.filter(o => o.is_correct).length;
      if (correctCount !== 1) {
        setErrorMsg('Round 1 MCQ questions must have exactly 1 correct option selected.');
        return;
      }
    } else {
      if (!formData.test_cases || formData.test_cases.length === 0) {
        setErrorMsg('Coding & Debugging questions require at least 1 test case.');
        return;
      }
      if (formData.test_cases.some(tc => !tc.expected_output.trim())) {
        setErrorMsg('Expected output is required for all test cases.');
        return;
      }
    }

    setSaving(true);
    try {
      if (editingQuestion) {
        await fetchApi(`/admin/questions/${editingQuestion.id}`, {
          method: 'PUT',
          body: JSON.stringify(formData),
        });
        setSuccessMsg(`Question "${formData.title}" updated successfully.`);
      } else {
        await fetchApi('/admin/questions', {
          method: 'POST',
          body: JSON.stringify(formData),
        });
        setSuccessMsg(`Question "${formData.title}" created successfully.`);
      }

      setIsModalOpen(false);
      await loadQuestions();
    } catch (e: any) {
      setErrorMsg(e.message || 'Failed to save question.');
    } finally {
      setSaving(false);
    }
  };

  const handleDuplicate = async (q: QuestionItem) => {
    try {
      await fetchApi(`/admin/questions/${q.id}/duplicate`, { method: 'POST' });
      setSuccessMsg(`Duplicated question "${q.title}" successfully.`);
      await loadQuestions();
    } catch (e: any) {
      setErrorMsg(e.message || 'Failed to duplicate question.');
    }
  };

  const handleConfirmDelete = async () => {
    if (!deletingQuestion) return;
    try {
      await fetchApi(`/admin/questions/${deletingQuestion.id}`, { method: 'DELETE' });
      setSuccessMsg(`Question "${deletingQuestion.title}" deleted.`);
      setIsDeleteOpen(false);
      setDeletingQuestion(null);
      await loadQuestions();
    } catch (e: any) {
      setErrorMsg(e.message || 'Failed to delete question.');
    }
  };

  // Filtered Questions
  const filteredQuestions = questions.filter(q => {
    if (selectedRound !== 0 && q.round_id !== selectedRound) return false;
    if (selectedCategory !== 'all' && q.category !== selectedCategory) return false;
    if (selectedDifficulty !== 'all' && q.difficulty !== selectedDifficulty) return false;
    if (searchQuery.trim()) {
      const s = searchQuery.toLowerCase();
      const matchTitle = q.title.toLowerCase().includes(s);
      const matchDesc = q.description.toLowerCase().includes(s);
      if (!matchTitle && !matchDesc) return false;
    }
    return true;
  });

  const categories = Array.from(new Set(questions.map(q => q.category).filter(Boolean))) as string[];

  if (isLoading || loading) {
    return (
      <div className="py-20 text-center flex flex-col items-center justify-center space-y-4">
        <RefreshCw className="w-8 h-8 text-purple-500 animate-spin" />
        <span className="text-purple-400 font-mono text-sm">Loading Question Bank...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 py-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
            <FileCode className="w-8 h-8 text-purple-500" />
            Question Bank Management
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Create, edit, duplicate, and configure questions with test cases across all 3 competition rounds.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => handleOpenAdd(selectedRound > 0 ? selectedRound : 1)}
            className="px-4 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-purple-600/30 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Add New Question
          </button>
        </div>
      </div>

      {/* Notifications */}
      {successMsg && (
        <div className="p-4 bg-emerald-950/80 border border-emerald-800 rounded-2xl flex items-center justify-between text-emerald-300 text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            <span>{successMsg}</span>
          </div>
          <button onClick={() => setSuccessMsg(null)} className="text-emerald-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-rose-950/80 border border-rose-800 rounded-2xl flex items-center justify-between text-rose-300 text-sm">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="bg-gray-900 border border-gray-800 rounded-3xl p-4 sm:p-6 shadow-xl space-y-4">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
          
          {/* Round Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-2 lg:pb-0">
            {[
              { id: 0, label: 'All Rounds' },
              { id: 1, label: 'Round 1 (MCQ)' },
              { id: 2, label: 'Round 2 (Debugging)' },
              { id: 3, label: 'Round 3 (Coding)' }
            ].map(r => (
              <button
                key={r.id}
                onClick={() => setSelectedRound(r.id)}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold border whitespace-nowrap transition-all cursor-pointer ${
                  selectedRound === r.id
                    ? 'bg-purple-600 border-purple-500 text-white shadow-md shadow-purple-600/30'
                    : 'bg-gray-950 border-gray-800 text-gray-400 hover:text-white hover:border-gray-700'
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>

          {/* Search & Filter Controls */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search title or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-950 border border-gray-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
              />
            </div>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-gray-950 border border-gray-800 rounded-xl px-3 py-2 text-xs text-gray-300 focus:outline-none focus:border-purple-500"
            >
              <option value="all">All Categories</option>
              {categories.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>

            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="bg-gray-950 border border-gray-800 rounded-xl px-3 py-2 text-xs text-gray-300 focus:outline-none focus:border-purple-500"
            >
              <option value="all">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>
        </div>

        {/* Stats bar */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-800/60 text-xs font-mono text-gray-400">
          <span>Showing <strong className="text-purple-400">{filteredQuestions.length}</strong> of {questions.length} Questions</span>
          <span>Total Marks Pool: <strong className="text-emerald-400">{filteredQuestions.reduce((acc, q) => acc + q.marks, 0)} pts</strong></span>
        </div>
      </div>

      {/* Questions List */}
      <div className="space-y-4">
        {filteredQuestions.length === 0 ? (
          <div className="bg-gray-900 border border-gray-800 rounded-3xl p-12 text-center text-gray-500 space-y-3">
            <HelpCircle className="w-12 h-12 text-gray-600 mx-auto" />
            <p className="text-sm font-semibold text-gray-400">No questions match the current filters.</p>
            <button
              onClick={() => handleOpenAdd(selectedRound > 0 ? selectedRound : 1)}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold transition-all cursor-pointer"
            >
              Create Question Now
            </button>
          </div>
        ) : (
          filteredQuestions.map((q, idx) => (
            <div 
              key={q.id} 
              className="bg-gray-900 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-lg"
            >
              <div className="space-y-2 flex-1">
                <div className="flex items-center flex-wrap gap-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    q.round_id === 1 ? 'bg-blue-950 text-blue-400 border border-blue-800' :
                    q.round_id === 2 ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                    'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  }`}>
                    Round {q.round_id}
                  </span>

                  <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 text-[10px] font-mono font-semibold">
                    {q.category || 'General'}
                  </span>

                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    q.difficulty === 'Easy' ? 'bg-emerald-900/40 text-emerald-400' :
                    q.difficulty === 'Hard' ? 'bg-rose-900/40 text-rose-400' :
                    'bg-amber-900/40 text-amber-400'
                  }`}>
                    {q.difficulty}
                  </span>

                  <span className="text-xs font-mono text-gray-500">Language: {q.language}</span>
                </div>

                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span className="text-purple-400 font-mono text-sm">#{q.order_index}</span>
                  {q.title}
                </h3>

                <p className="text-xs text-gray-400 line-clamp-2">{q.description}</p>
              </div>

              {/* Badges & Action Buttons */}
              <div className="flex items-center gap-4 self-end md:self-center">
                <div className="text-right font-mono text-xs hidden sm:block">
                  <div className="text-emerald-400 font-bold">+{q.marks} pts</div>
                  {q.negative_marks > 0 && (
                    <div className="text-rose-400 text-[10px]">-{q.negative_marks} neg</div>
                  )}
                  <div className="text-gray-500 text-[10px]">
                    {q.round_id === 1 ? `${q.options?.length || 0} Options` : `${q.test_cases?.length || 0} Test Cases`}
                  </div>
                </div>

                <div className="flex items-center gap-1.5 bg-gray-950 p-1.5 rounded-xl border border-gray-800">
                  <button
                    onClick={() => { setViewingQuestion(q); setIsDetailOpen(true); }}
                    title="View Details"
                    className="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-800 rounded-lg transition-colors cursor-pointer"
                  >
                    <Eye className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => handleOpenEdit(q)}
                    title="Edit Question"
                    className="p-2 text-gray-400 hover:text-amber-400 hover:bg-gray-800 rounded-lg transition-colors cursor-pointer"
                  >
                    <Edit3 className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => handleDuplicate(q)}
                    title="Duplicate Question"
                    className="p-2 text-gray-400 hover:text-purple-400 hover:bg-gray-800 rounded-lg transition-colors cursor-pointer"
                  >
                    <Copy className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => { setDeletingQuestion(q); setIsDeleteOpen(true); }}
                    title="Delete Question"
                    className="p-2 text-gray-400 hover:text-rose-400 hover:bg-gray-800 rounded-lg transition-colors cursor-pointer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* --- ADD / EDIT QUESTION MODAL --- */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-gray-900 border border-gray-800 rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-6 shadow-2xl">
            
            <div className="flex items-center justify-between border-b border-gray-800 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                {editingQuestion ? <Edit3 className="w-5 h-5 text-amber-400" /> : <Plus className="w-5 h-5 text-purple-400" />}
                {editingQuestion ? `Edit Question #${editingQuestion.id}` : 'Create New Question'}
              </h2>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            {errorMsg && (
              <div className="p-3 bg-rose-950/80 border border-rose-800 rounded-xl text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="space-y-4 text-xs">
              {/* Round Selector & Basics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block font-bold text-gray-300 mb-1">Target Round *</label>
                  <select
                    value={formData.round_id}
                    onChange={(e) => setFormData({ ...formData, round_id: parseInt(e.target.value) })}
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-white focus:border-purple-500"
                  >
                    <option value={1}>Round 1 (MCQ)</option>
                    <option value={2}>Round 2 (Debugging)</option>
                    <option value={3}>Round 3 (Algorithmic Coding)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold text-gray-300 mb-1">Category</label>
                  <input
                    type="text"
                    placeholder="e.g. DSA, OOP, Python"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-white focus:border-purple-500"
                  />
                </div>

                <div>
                  <label className="block font-bold text-gray-300 mb-1">Difficulty</label>
                  <select
                    value={formData.difficulty}
                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-white focus:border-purple-500"
                  >
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold text-gray-300 mb-1">Primary Language</label>
                  <select
                    value={formData.language}
                    onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-white focus:border-purple-500"
                  >
                    <option value="python">Python 3</option>
                    <option value="c">C</option>
                    <option value="cpp">C++</option>
                    <option value="java">Java</option>
                  </select>
                </div>
              </div>

              {/* Title & Marks */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="md:col-span-2">
                  <label className="block font-bold text-gray-300 mb-1">Question Title *</label>
                  <input
                    type="text"
                    placeholder="Short title for question"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-white focus:border-purple-500"
                  />
                </div>

                <div>
                  <label className="block font-bold text-gray-300 mb-1">Marks (+)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.marks}
                    onChange={(e) => setFormData({ ...formData, marks: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-white focus:border-purple-500"
                  />
                </div>

                <div>
                  <label className="block font-bold text-gray-300 mb-1">Negative Marks (-)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.negative_marks}
                    onChange={(e) => setFormData({ ...formData, negative_marks: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-white focus:border-purple-500"
                  />
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block font-bold text-gray-300 mb-1">Problem Description / Question Text *</label>
                <textarea
                  rows={3}
                  placeholder="Detailed description of the question..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-white focus:border-purple-500"
                />
              </div>

              {/* Code Snippet (Buggy code or Initial code) */}
              <div>
                <label className="block font-bold text-gray-300 mb-1">
                  {formData.round_id === 2 ? 'Buggy Starter Code (Round 2)' : 'Code Snippet / Starter Template (Optional)'}
                </label>
                <textarea
                  rows={4}
                  placeholder="# Enter code snippet or starter code here"
                  value={formData.code_snippet}
                  onChange={(e) => setFormData({ ...formData, code_snippet: e.target.value })}
                  className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2.5 text-purple-300 font-mono focus:border-purple-500"
                />
              </div>

              {/* ROUND 1: MCQ OPTIONS BUILDER */}
              {formData.round_id === 1 && (
                <div className="bg-gray-950 border border-gray-800 rounded-2xl p-4 space-y-3">
                  <h4 className="font-bold text-purple-400 flex items-center justify-between">
                    <span>MCQ Options (Select the 1 Correct Answer)</span>
                    <span className="text-[10px] text-gray-500 font-normal">Exactly 1 option must be correct</span>
                  </h4>

                  <div className="space-y-2.5">
                    {formData.options.map((opt, idx) => (
                      <div key={idx} className="flex items-center gap-3 bg-gray-900 p-2.5 rounded-xl border border-gray-800">
                        <input
                          type="radio"
                          name="correct_option"
                          checked={opt.is_correct}
                          onChange={() => {
                            const updated = formData.options.map((o, i) => ({
                              ...o,
                              is_correct: i === idx
                            }));
                            setFormData({ ...formData, options: updated });
                          }}
                          className="w-4 h-4 text-purple-600 focus:ring-purple-500 cursor-pointer"
                        />
                        <span className="font-mono font-bold text-white w-6">{opt.option_key}.</span>
                        <input
                          type="text"
                          placeholder={`Option ${opt.option_key} text...`}
                          value={opt.option_text}
                          onChange={(e) => {
                            const updated = [...formData.options];
                            updated[idx].option_text = e.target.value;
                            setFormData({ ...formData, options: updated });
                          }}
                          className="flex-1 bg-gray-950 border border-gray-800 rounded-lg px-3 py-1.5 text-white focus:border-purple-500"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ROUND 2 & 3: INPUT FORMAT, CONSTRAINTS, SAMPLE I/O */}
              {(formData.round_id === 2 || formData.round_id === 3) && (
                <div className="space-y-4 border-t border-gray-800 pt-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block font-bold text-gray-300 mb-1">Input Format</label>
                      <textarea
                        rows={2}
                        value={formData.input_format}
                        onChange={(e) => setFormData({ ...formData, input_format: e.target.value })}
                        className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2 text-white"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-gray-300 mb-1">Output Format</label>
                      <textarea
                        rows={2}
                        value={formData.output_format}
                        onChange={(e) => setFormData({ ...formData, output_format: e.target.value })}
                        className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2 text-white"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-gray-300 mb-1">Constraints</label>
                      <textarea
                        rows={2}
                        value={formData.constraints}
                        onChange={(e) => setFormData({ ...formData, constraints: e.target.value })}
                        className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2 text-white"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block font-bold text-gray-300 mb-1">Sample Input</label>
                      <textarea
                        rows={2}
                        value={formData.sample_input}
                        onChange={(e) => setFormData({ ...formData, sample_input: e.target.value })}
                        className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2 font-mono text-white"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-gray-300 mb-1">Sample Output</label>
                      <textarea
                        rows={2}
                        value={formData.sample_output}
                        onChange={(e) => setFormData({ ...formData, sample_output: e.target.value })}
                        className="w-full bg-gray-950 border border-gray-800 rounded-xl p-2 font-mono text-white"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* DYNAMIC TEST CASE BUILDER (ROUND 2 & 3) */}
              {(formData.round_id === 2 || formData.round_id === 3) && (
                <div className="bg-gray-950 border border-gray-800 rounded-2xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-emerald-400">Test Cases Suite (Judge0 Execution)</h4>
                    <button
                      type="button"
                      onClick={() => {
                        setFormData({
                          ...formData,
                          test_cases: [
                            ...formData.test_cases,
                            { input_data: '', expected_output: '', is_hidden: true, weight: 1.0 }
                          ]
                        });
                      }}
                      className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-[11px] flex items-center gap-1 cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" /> Add Test Case
                    </button>
                  </div>

                  <div className="space-y-3">
                    {formData.test_cases.map((tc, idx) => (
                      <div key={idx} className="bg-gray-900 border border-gray-800 rounded-xl p-3 space-y-2">
                        <div className="flex items-center justify-between text-[11px] font-mono text-gray-400">
                          <span className="font-bold text-purple-400">Test Case #{idx + 1}</span>
                          <div className="flex items-center gap-4">
                            <label className="flex items-center gap-1.5 cursor-pointer">
                              <input
                                type="checkbox"
                                checked={tc.is_hidden}
                                onChange={(e) => {
                                  const updated = [...formData.test_cases];
                                  updated[idx].is_hidden = e.target.checked;
                                  setFormData({ ...formData, test_cases: updated });
                                }}
                                className="w-3.5 h-3.5 rounded text-purple-600"
                              />
                              <span>Hidden Test Case</span>
                            </label>

                            {formData.test_cases.length > 1 && (
                              <button
                                type="button"
                                onClick={() => {
                                  const updated = formData.test_cases.filter((_, i) => i !== idx);
                                  setFormData({ ...formData, test_cases: updated });
                                }}
                                className="text-rose-400 hover:text-white"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          <div>
                            <span className="block text-[10px] text-gray-500 mb-0.5">Input Data (stdin):</span>
                            <textarea
                              rows={2}
                              value={tc.input_data}
                              onChange={(e) => {
                                const updated = [...formData.test_cases];
                                updated[idx].input_data = e.target.value;
                                setFormData({ ...formData, test_cases: updated });
                              }}
                              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-2 font-mono text-white text-xs"
                            />
                          </div>

                          <div>
                            <span className="block text-[10px] text-gray-500 mb-0.5">Expected Output (stdout):</span>
                            <textarea
                              rows={2}
                              value={tc.expected_output}
                              onChange={(e) => {
                                const updated = [...formData.test_cases];
                                updated[idx].expected_output = e.target.value;
                                setFormData({ ...formData, test_cases: updated });
                              }}
                              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-2 font-mono text-white text-xs"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-3 border-t border-gray-800 pt-4">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveQuestion}
                disabled={saving}
                className="px-5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-purple-600/30 flex items-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                {editingQuestion ? 'Save Changes' : 'Create Question'}
              </button>
            </div>

          </div>
        </div>
      )}

      {/* --- VIEW DETAILS MODAL --- */}
      {isDetailOpen && viewingQuestion && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-gray-900 border border-gray-800 rounded-3xl max-w-3xl w-full max-h-[85vh] overflow-y-auto p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-gray-800 pb-4">
              <div>
                <span className="text-xs font-mono text-purple-400 font-bold">Round {viewingQuestion.round_id} Question Details</span>
                <h2 className="text-xl font-bold text-white">{viewingQuestion.title}</h2>
              </div>
              <button onClick={() => setIsDetailOpen(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="flex items-center gap-4 bg-gray-950 p-3 rounded-xl border border-gray-800 font-mono">
                <div>Category: <strong className="text-purple-400">{viewingQuestion.category}</strong></div>
                <div>Difficulty: <strong className="text-amber-400">{viewingQuestion.difficulty}</strong></div>
                <div>Marks: <strong className="text-emerald-400">+{viewingQuestion.marks}</strong></div>
              </div>

              <div>
                <h4 className="font-bold text-gray-400 mb-1">Description:</h4>
                <p className="text-gray-300 bg-gray-950 p-3 rounded-xl border border-gray-800 whitespace-pre-line">
                  {viewingQuestion.description}
                </p>
              </div>

              {viewingQuestion.code_snippet && (
                <div>
                  <h4 className="font-bold text-gray-400 mb-1">Code Snippet:</h4>
                  <pre className="bg-gray-950 p-3 rounded-xl border border-gray-800 font-mono text-purple-300 overflow-x-auto">
                    {viewingQuestion.code_snippet}
                  </pre>
                </div>
              )}

              {viewingQuestion.round_id === 1 && viewingQuestion.options && (
                <div>
                  <h4 className="font-bold text-gray-400 mb-2">Options:</h4>
                  <div className="space-y-2">
                    {viewingQuestion.options.map((opt, i) => (
                      <div 
                        key={i} 
                        className={`p-3 rounded-xl border flex items-center justify-between font-mono ${
                          opt.is_correct ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300' : 'bg-gray-950 border-gray-800 text-gray-400'
                        }`}
                      >
                        <span><strong>{opt.option_key}.</strong> {opt.option_text}</span>
                        {opt.is_correct && <span className="text-[10px] font-bold uppercase bg-emerald-900 px-2 py-0.5 rounded">Correct</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {(viewingQuestion.round_id === 2 || viewingQuestion.round_id === 3) && viewingQuestion.test_cases && (
                <div>
                  <h4 className="font-bold text-gray-400 mb-2">Test Cases ({viewingQuestion.test_cases.length}):</h4>
                  <div className="space-y-2">
                    {viewingQuestion.test_cases.map((tc, i) => (
                      <div key={i} className="bg-gray-950 p-3 rounded-xl border border-gray-800 font-mono space-y-1 text-[11px]">
                        <div className="flex items-center justify-between text-purple-400">
                          <span>Test Case #{i + 1}</span>
                          <span className={tc.is_hidden ? 'text-amber-400' : 'text-emerald-400'}>
                            {tc.is_hidden ? 'Hidden' : 'Public'}
                          </span>
                        </div>
                        <div>Input: <code className="text-gray-300">{tc.input_data || '(empty)'}</code></div>
                        <div>Expected Output: <code className="text-emerald-300">{tc.expected_output}</code></div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-end pt-4 border-t border-gray-800">
              <button
                onClick={() => setIsDetailOpen(false)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- DELETE CONFIRMATION MODAL --- */}
      {isDeleteOpen && deletingQuestion && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-800 rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-rose-500">
              <AlertTriangle className="w-6 h-6" />
              <h3 className="text-lg font-bold text-white">Delete Question?</h3>
            </div>

            <p className="text-xs text-gray-400 leading-relaxed">
              Are you sure you want to delete question <strong className="text-white">"{deletingQuestion.title}"</strong>? 
              This action will permanently remove all associated options, test cases, and submissions for this question.
            </p>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setIsDeleteOpen(false)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-xs font-bold cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold transition-all cursor-pointer shadow-lg shadow-rose-600/30"
              >
                Delete Question
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
