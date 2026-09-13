import Link from 'next/link';
import { Terminal, Code, Cpu } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-[#060910] border-t border-gray-800 text-gray-400 text-sm py-8 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-blue-500" />
          <span className="font-bold text-white">Engineering Day Coding Challenge 2026</span>
        </div>
        <p className="text-xs text-gray-500 text-center sm:text-left">
          Production Competitive Programming Platform for College Contest Organization.
        </p>
        <div className="flex items-center gap-4 text-xs font-mono text-gray-400">
          <span className="flex items-center gap-1"><Code className="w-3.5 h-3.5 text-emerald-400" /> Next.js 15</span>
          <span className="flex items-center gap-1"><Cpu className="w-3.5 h-3.5 text-blue-400" /> Judge0</span>
        </div>
      </div>
    </footer>
  );
}
