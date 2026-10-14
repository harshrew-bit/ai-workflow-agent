import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Copy, Check } from 'lucide-react';
import { ExecutionReport } from '../types/workflow';

interface RawJsonViewerProps {
  report: ExecutionReport | null;
}

export const RawJsonViewer: React.FC<RawJsonViewerProps> = ({ report }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!report) return null;

  const jsonString = JSON.stringify(report, null, 2);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(jsonString);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      // Fallback
    }
  };

  return (
    <div className="mt-4 bg-cream-50 rounded-xl border border-charcoal-100 shadow-warm overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 text-left font-mono text-xs text-charcoal-700 hover:bg-cream-200 transition-colors"
      >
        <div className="flex items-center space-x-2">
          {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          <span className="font-semibold">Technical details (Raw ExecutionReport JSON)</span>
        </div>
        <span className="text-[10px] text-charcoal-400">
          {isOpen ? 'Click to collapse' : 'Click to expand'}
        </span>
      </button>

      {isOpen && (
        <div className="border-t border-charcoal-100 p-4 bg-charcoal-900 text-cream-50 relative">
          <div className="flex justify-end mb-2">
            <button
              onClick={handleCopy}
              className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-charcoal-800 hover:bg-charcoal-700 text-charcoal-300 hover:text-cream-50 text-[11px] font-mono border border-charcoal-700 transition-all"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy JSON</span>
                </>
              )}
            </button>
          </div>
          <pre className="text-xs font-mono overflow-x-auto p-2 bg-charcoal-950/60 rounded border border-charcoal-800 leading-relaxed text-charcoal-200 max-h-96">
            <code>{jsonString}</code>
          </pre>
        </div>
      )}
    </div>
  );
};
