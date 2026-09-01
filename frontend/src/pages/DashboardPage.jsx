import React, { useEffect, useState } from 'react';
import { 
  FolderGit2, 
  Globe, 
  FileCheck2, 
  AlertTriangle, 
  Play, 
  CheckCircle, 
  PlusCircle, 
  ArrowRight,
  Sparkles,
  Search
} from 'lucide-react';
import { api } from '../api/client';

export default function DashboardPage({ setActiveTab, onSelectProject }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quickQuery, setQuickQuery] = useState('');

  const loadStats = () => {
    setLoading(true);
    api.getStats()
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadStats();
  }, []);

  const handleQuickLaunch = (e) => {
    e.preventDefault();
    if (!quickQuery.trim()) return;
    api.createProject({ question: quickQuery.trim() })
      .then(proj => {
        onSelectProject(proj.id);
        setActiveTab('tracker');
      })
      .catch(err => alert(`Failed to launch: ${err.message}`));
  };

  if (loading) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading Executive Dashboard...</div>;
  }

  return (
    <div className="page-wrapper">
      {/* Quick Launch Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9))', border: '1px solid rgba(59, 130, 246, 0.4)', padding: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-cyan)', fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
          <Sparkles size={16} /> Autonomous Research Engine
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'white', marginBottom: '0.5rem' }}>
          What enterprise research question would you like to investigate today?
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.5rem', maxWidth: '800px' }}>
          Enter any research question. The agent will autonomously create subtopics, search public web & academic databases, evaluate source reliability, extract verbatim evidence, detect contradictions, and synthesize traceable conclusions.
        </p>

        <form onSubmit={handleQuickLaunch} style={{ display: 'flex', gap: '0.75rem', maxWidth: '900px' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={quickQuery}
              onChange={e => setQuickQuery(e.target.value)}
              placeholder="e.g. What AI technologies are changing retail supply chains?"
              style={{
                width: '100%',
                background: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                padding: '0.85rem 1rem 0.85rem 2.75rem',
                color: 'white',
                fontSize: '0.95rem',
                outline: 'none'
              }}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ padding: '0.85rem 1.5rem' }}>
            <PlusCircle size={18} />
            <span>Start New Research</span>
          </button>
        </form>
      </div>

      {/* Metric Cards Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: 'var(--accent-blue)' }}>
            <FolderGit2 size={24} />
          </div>
          <div className="metric-info">
            <div className="label">Total Research Projects</div>
            <div className="value">{stats?.total_projects || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)' }}>
            <Globe size={24} />
          </div>
          <div className="metric-info">
            <div className="label">Sources Collected</div>
            <div className="value">{stats?.total_sources || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)' }}>
            <FileCheck2 size={24} />
          </div>
          <div className="metric-info">
            <div className="label">Findings Extracted</div>
            <div className="value">{stats?.total_findings || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)' }}>
            <Play size={24} />
          </div>
          <div className="metric-info">
            <div className="label">Research Running</div>
            <div className="value">{stats?.running_projects || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(139, 92, 246, 0.15)', color: 'var(--accent-purple)' }}>
            <CheckCircle size={24} />
          </div>
          <div className="metric-info">
            <div className="label">Completed Research</div>
            <div className="value">{stats?.completed_projects || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(244, 63, 94, 0.15)', color: 'var(--accent-rose)' }}>
            <AlertTriangle size={24} />
          </div>
          <div className="metric-info">
            <div className="label">Contradictions Detected</div>
            <div className="value">{stats?.total_contradictions || 0}</div>
          </div>
        </div>
      </div>

      {/* Recent Research Questions Table */}
      <div className="card">
        <div className="card-title">
          <span>Recent Research Projects</span>
          <button 
            onClick={() => setActiveTab('history')} 
            style={{ background: 'none', border: 'none', color: 'var(--accent-blue)', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
          >
            <span>View All History</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {(!stats?.recent_projects || stats.recent_projects.length === 0) ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No research projects found. Click "Start New Research" above to run your first project!
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Research Question</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Sources</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Findings</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Conclusions</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_projects.map(p => (
                  <tr key={p.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '1rem', fontWeight: 600, color: 'white', maxWidth: '400px' }}>
                      {p.question}
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span className={`badge badge-${p.status === 'completed' ? 'completed' : p.status === 'running' ? 'running' : 'medium'}`}>
                        {p.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{p.sources_count}</td>
                    <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{p.findings_count}</td>
                    <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{p.conclusions_count}</td>
                    <td style={{ padding: '1rem' }}>
                      <button
                        onClick={() => {
                          onSelectProject(p.id);
                          setActiveTab(p.status === 'running' ? 'tracker' : 'results');
                        }}
                        className="btn btn-secondary"
                        style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
                      >
                        <span>{p.status === 'running' ? 'View Live Progress' : 'Explore Results'}</span>
                        <ArrowRight size={12} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
