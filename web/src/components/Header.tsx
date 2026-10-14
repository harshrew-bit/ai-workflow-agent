import React from 'react';
import { Network, Cpu, BookOpen, GitMerge, CheckCircle2, ShieldCheck, Activity } from 'lucide-react';
import { HealthResponse } from '../types/workflow';

interface HeaderProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  health: HealthResponse | null;
  isDemoMode: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onSelectTab,
  health,
  isDemoMode,
}) => {
  const navItems = [
    { id: 'home', label: 'Home', icon: Activity },
    { id: 'architecture', label: 'Architecture', icon: GitMerge },
    { id: 'workbook', label: 'Workbook', icon: BookOpen },
    { id: 'decisions', label: 'Decisions', icon: ShieldCheck },
    { id: 'extending', label: 'Extending', icon: Network },
    { id: 'status', label: 'Status', icon: CheckCircle2 },
  ];

  return (
    <header className="border-b border-charcoal-100 bg-cream-50/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Product Identity */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectTab('home')}>
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-brand-blue to-brand-magenta p-0.5 shadow-sm flex items-center justify-center">
              <div className="w-full h-full bg-cream-50 rounded-[7px] flex items-center justify-center">
                <Cpu className="w-5 h-5 text-brand-blue" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base tracking-tight text-charcoal-900">
                  AI Workflow Agent
                </span>
                <span className="hidden sm:inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-blush-200 text-charcoal-700 border border-blush-300">
                  v0.1.0
                </span>
              </div>
              <p className="hidden md:block text-[10px] font-mono tracking-wider text-charcoal-500 uppercase">
                Excel Workflows · Python · Agent Execution
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-1" aria-label="Main Navigation">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-charcoal-900 text-cream-50 shadow-sm'
                      : 'text-charcoal-600 hover:text-charcoal-900 hover:bg-cream-200'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Real-time Status Badge */}
          <div className="flex items-center space-x-2">
            {health && !isDemoMode ? (
              <div
                className="flex items-center space-x-2 px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-emerald-50 text-emerald-800 border border-emerald-200 shadow-sm"
                title={`FastAPI backend active on port 8000 (${health.workflow_count} workflows loaded)`}
              >
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="hidden sm:inline">Backend connected</span>
                <span className="sm:hidden">Online</span>
              </div>
            ) : (
              <div
                className="flex items-center space-x-2 px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-amber-50 text-amber-800 border border-amber-300 shadow-sm"
                title="Running in Demo Mode: inspecting genuine saved outputs from examples/output/"
              >
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                <span>Demo mode</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Navigation bar */}
      <div className="md:hidden border-t border-charcoal-100 bg-cream-100 px-2 py-2 flex justify-around">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex flex-col items-center py-1 px-2 text-[10px] font-medium rounded ${
                isActive ? 'text-brand-blue font-semibold' : 'text-charcoal-500'
              }`}
            >
              <Icon className="w-4 h-4 mb-0.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};
