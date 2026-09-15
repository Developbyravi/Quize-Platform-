"use client";

import { useEffect, useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { Save, CheckCircle2 } from 'lucide-react';

interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
  language: string;
  onLanguageChange?: (lang: string) => void;
  onAutosave?: (code: string) => void;
  readOnly?: boolean;
}

const MONACO_LANG_MAP: Record<string, string> = {
  c: "cpp",
  cpp: "cpp",
  java: "java",
  python: "python",
  py: "python"
};

export default function CodeEditor({
  code,
  onChange,
  language,
  onLanguageChange,
  onAutosave,
  readOnly = false,
}: CodeEditorProps) {
  const [lastSaved, setLastSaved] = useState<string>('');
  const [isSaved, setIsSaved] = useState<boolean>(true);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const handleEditorChange = (val?: string) => {
    const newCode = val || '';
    onChange(newCode);
    setIsSaved(false);

    if (readOnly || !onAutosave) return;

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      onAutosave(newCode);
      setIsSaved(true);
      setLastSaved(new Date().toLocaleTimeString());
    }, 2500);
  };

  return (
    <div className="flex flex-col h-full bg-[#0d1117] border border-gray-800 rounded-xl overflow-hidden shadow-xl">
      {/* Editor Header Bar */}
      <div className="bg-[#161b22] px-4 py-2 border-b border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-semibold text-gray-400 uppercase">Monaco Code Editor</span>
          {onLanguageChange && (
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="bg-gray-900 border border-gray-700 text-xs font-mono text-blue-400 px-2 py-1 rounded-md focus:outline-none focus:border-blue-500"
              disabled={readOnly}
            >
              <option value="python">Python 3</option>
              <option value="cpp">C++ (GCC 14)</option>
              <option value="c">C (GCC 11)</option>
              <option value="java">Java (OpenJDK 13)</option>
            </select>
          )}
        </div>

        {/* Autosave Status Indicator */}
        {!readOnly && (
          <div className="flex items-center gap-1.5 text-xs text-gray-400 font-mono">
            {isSaved ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400">Autosaved</span>
                {lastSaved && <span className="text-gray-500">at {lastSaved}</span>}
              </>
            ) : (
              <>
                <Save className="w-3.5 h-3.5 text-amber-400 animate-bounce" />
                <span className="text-amber-400">Saving draft...</span>
              </>
            )}
          </div>
        )}
      </div>

      {/* Editor Main Canvas */}
      <div className="flex-1 min-h-[400px]">
        <Editor
          height="100%"
          language={MONACO_LANG_MAP[language.toLowerCase()] || "python"}
          theme="vs-dark"
          value={code}
          onChange={handleEditorChange}
          options={{
            readOnly,
            fontSize: 14,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            lineNumbers: "on",
            padding: { top: 10 },
          }}
        />
      </div>
    </div>
  );
}
