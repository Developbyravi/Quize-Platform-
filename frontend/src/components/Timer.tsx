"use client";

import { useEffect, useState } from 'react';
import { Clock, AlertTriangle } from 'lucide-react';

interface TimerProps {
  initialSeconds: number;
  onExpire?: () => void;
}

export default function Timer({ initialSeconds, onExpire }: TimerProps) {
  const [secondsLeft, setSecondsLeft] = useState<number>(initialSeconds);

  useEffect(() => {
    setSecondsLeft(initialSeconds);
  }, [initialSeconds]);

  useEffect(() => {
    if (secondsLeft <= 0) {
      if (onExpire) onExpire();
      return;
    }

    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          if (onExpire) onExpire();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [secondsLeft, onExpire]);

  const minutes = Math.floor(secondsLeft / 60);
  const secs = secondsLeft % 60;
  const isUrgent = secondsLeft < 300; // Less than 5 mins

  return (
    <div
      className={`flex items-center gap-2 px-4 py-2 rounded-xl font-mono text-lg font-bold border transition-colors ${
        isUrgent
          ? 'bg-red-950/50 border-red-600 text-red-400 animate-pulse'
          : 'bg-gray-900 border-gray-700 text-blue-400'
      }`}
    >
      {isUrgent ? <AlertTriangle className="w-5 h-5 text-red-500" /> : <Clock className="w-5 h-5 text-blue-400" />}
      <span>
        {String(minutes).padStart(2, '0')}:{String(secs).padStart(2, '0')}
      </span>
      <span className="text-xs font-sans text-gray-400 font-normal uppercase ml-1">Left</span>
    </div>
  );
}
