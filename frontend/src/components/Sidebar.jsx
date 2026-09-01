import React from 'react';
import { 
  LayoutDashboard, 
  PlusCircle, 
  Database, 
  History, 
  Cpu,
  Sparkles,
  User,
  Mail
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

      {/* Developer Attribution Card */}
      <div style={{ padding: '0.75rem', borderTop: '1px solid var(--border-color)', margin: '0.5rem' }}>
        <div style={{ background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8))', padding: '0.85rem', borderRadius: '10px', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.35rem' }}>
            <User size={14} style={{ color: 'var(--accent-cyan)' }} />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'white' }}>Built by Jay Beedkar</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
            <Mail size={12} style={{ color: 'var(--accent-blue)' }} />
            <a href="mailto:jayudict@gmail.com" style={{ color: 'var(--accent-cyan)', textDecoration: 'none', fontWeight: 500 }}>
              jayudict@gmail.com
            </a>
          </div>
        </div>
      </div>
    </aside>
  );
}
