"use client";

import { CheckCircle2, Bookmark, Circle } from 'lucide-react';

interface QuestionPaletteProps {
  totalQuestions: number;
  currentIndex: number;
  answers: Record<number, { selected_option: string | null; is_marked_for_review: boolean }>;
  onSelect: (index: number) => void;
}

export default function QuestionPalette({
  totalQuestions,
  currentIndex,
  answers,
  onSelect,
}: QuestionPaletteProps) {
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-4 shadow-xl">
      <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider mb-3">Question Palette</h3>

      {/* Grid Palette */}
      <div className="grid grid-cols-5 gap-2 mb-6">
        {Array.from({ length: totalQuestions }, (_, i) => {
          const qId = i + 1;
          const ans = answers[qId];
          const isAnswered = ans && ans.selected_option !== null;
          const isMarked = ans && ans.is_marked_for_review;
          const isCurrent = currentIndex === i;

          let btnClass = "bg-gray-800 text-gray-400 border-gray-700 hover:bg-gray-700";
          if (isAnswered && isMarked) {
            btnClass = "bg-purple-900/80 text-purple-200 border-purple-500 font-bold";
          } else if (isAnswered) {
            btnClass = "bg-emerald-900/80 text-emerald-200 border-emerald-500 font-bold";
          } else if (isMarked) {
            btnClass = "bg-amber-900/80 text-amber-200 border-amber-500 font-bold";
          }

          if (isCurrent) {
            btnClass += " ring-2 ring-blue-500 scale-105";
          }

          return (
            <button
              key={qId}
              onClick={() => onSelect(i)}
              className={`h-10 rounded-lg border flex flex-col items-center justify-center text-xs font-mono transition-all ${btnClass}`}
            >
              <span>{qId}</span>
            </button>
          );
        })}
      </div>

      {/* Legend Indicators */}
      <div className="space-y-2 text-xs text-gray-400 font-medium pt-3 border-t border-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500" />
          <span>Answered</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-500" />
          <span>Answered & Marked</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-amber-500" />
          <span>Marked for Review</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-gray-700" />
          <span>Unanswered</span>
        </div>
      </div>
    </div>
  );
}
