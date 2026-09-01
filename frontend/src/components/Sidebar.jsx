import React from 'react';
import { 
  LayoutDashboard, 
  PlusCircle, 
  Database, 
  History, 
  Cpu,
  Sparkles
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'new-research', label: 'New Research', icon: PlusCircle },
    { id: 'knowledge-search', label: 'Knowledge Base', icon: Database },
    { id: 'history', label: 'Research History', icon: History }
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Cpu size={20} />
        </div>
        <div>
          <h1 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'white', lineHeight: 1.2 }}>
            Research Agent
          </h1>
          <p style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
            Enterprise AI Edition
          </p>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, padding: '0.5rem 1rem', letterSpacing: '0.05em' }}>
          Navigation
        </div>
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} style={{ color: isActive ? 'var(--accent-blue)' : 'var(--text-secondary)' }} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ padding: '1rem', borderTop: '1px solid var(--border-color)', margin: '0.5rem' }}>
        <div style={{ background: 'var(--bg-card)', padding: '0.85rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <Sparkles size={14} style={{ color: 'var(--accent-cyan)' }} />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'white' }}>AI Reasoning</span>
          </div>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            11-Stage Evidence Pipeline & Deterministic Reliability Scoring
          </p>
        </div>
      </div>
    </aside>
  );
}
