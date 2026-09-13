"use client";

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Terminal, Shield, Trophy, User, LogOut, LayoutDashboard, BookOpen } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-50 bg-[#090d16]/95 backdrop-blur-md border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-wide">
              Engineering Day <span className="text-blue-500">Coding Challenge</span>
            </h1>
            <p className="text-xs text-gray-400 font-mono">Engineering Day 2026</p>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-300">
          <Link href="/" className="hover:text-blue-400 transition-colors">Home</Link>
          <Link href="/rules" className="hover:text-blue-400 transition-colors flex items-center gap-1.5">
            <BookOpen className="w-4 h-4 text-gray-400" /> Rules
          </Link>
          <Link href="/leaderboard" className="hover:text-blue-400 transition-colors flex items-center gap-1.5">
            <Trophy className="w-4 h-4 text-amber-400" /> Leaderboard
          </Link>

          {user && user.role === 'participant' && (
            <Link href="/dashboard" className="text-blue-400 hover:text-blue-300 flex items-center gap-1.5 font-semibold">
              <LayoutDashboard className="w-4 h-4" /> Dashboard
            </Link>
          )}

          {user && user.role === 'admin' && (
            <Link href="/admin" className="text-purple-400 hover:text-purple-300 flex items-center gap-1.5 font-semibold">
              <Shield className="w-4 h-4" /> Admin Console
            </Link>
          )}
        </nav>

        {/* User Auth Buttons */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex flex-col text-right">
                <span className="text-sm font-semibold text-white">{user.full_name}</span>
                <span className="text-xs text-gray-400 capitalize">{user.role}</span>
              </div>
              <button
                onClick={logout}
                className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors flex items-center gap-1 text-sm font-medium"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors shadow-md shadow-blue-600/20"
              >
                Register
              </Link>
            </div>
          )}
        </div>

      </div>
    </header>
  );
}
