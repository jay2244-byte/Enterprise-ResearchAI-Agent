import React from 'react';
import { ShieldCheck, Plus, RefreshCw } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, systemStatus = 'healthy', onRefresh }) {
  const titles = {
    dashboard: 'Executive Research Dashboard',
    'new-research': 'Launch New Enterprise Research',
    'knowledge-search': 'Search Stored Research Knowledge Base',
    history: 'Historical Research Archive',
    results: 'Research Project Results & Evidence Trace',
    tracker: 'Live Research Execution Progress'
  };

  return (
    <header className="top-bar">
      <div>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'white' }}>
          {titles[activeTab] || 'Enterprise AI Research Agent'}
        </h2>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Autonomous Multi-Source Investigation, Reliability Evaluation & Contradiction Detection
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', background: 'rgba(16, 185, 129, 0.1)', color: '#34d399', padding: '0.3rem 0.75rem', borderRadius: '9999px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <ShieldCheck size={14} />
          <span>System Online</span>
        </div>

        {onRefresh && (
          <button onClick={onRefresh} className="btn btn-secondary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}>
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
        )}

        {activeTab !== 'new-research' && (
          <button 
            onClick={() => setActiveTab('new-research')}
            className="btn btn-primary"
            style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem' }}
          >
            <Plus size={16} />
            <span>Start New Research</span>
          </button>
        )}
      </div>
    </header>
  );
}
