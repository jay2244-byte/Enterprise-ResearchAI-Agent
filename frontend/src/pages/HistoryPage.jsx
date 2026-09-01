import React, { useEffect, useState } from 'react';
import { History, ArrowRight, Trash2, Search, Filter } from 'lucide-react';
import { api } from '../api/client';

export default function HistoryPage({ setActiveTab, onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  const loadProjects = () => {
    setLoading(true);
    api.listProjects(0, 50)
      .then(data => {
        setProjects(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this research project?")) return;
    try {
      await api.deleteProject(id);
      loadProjects();
    } catch (err) {
      alert(`Failed to delete: ${err.message}`);
    }
  };

  const filtered = projects.filter(p => {
    const matchesSearch = p.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (p.industry && p.industry.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = statusFilter === 'All' || p.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="page-wrapper">
      <div className="card">
        <div className="card-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <History size={20} style={{ color: 'var(--accent-blue)' }} />
            <span>Research History Archive ({filtered.length})</span>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            {/* Search Input */}
            <div style={{ position: 'relative' }}>
              <Search size={14} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                placeholder="Filter history..."
                style={{
                  background: 'var(--bg-primary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '0.35rem 0.65rem 0.35rem 2rem',
                  color: 'white',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              style={{
                background: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '0.35rem 0.65rem',
                color: 'white',
                fontSize: '0.8rem'
              }}
            >
              <option value="All">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="running">Running</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading history archive...</div>
        ) : filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No research projects match your search parameters.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>ID</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Research Question</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Date</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Sources</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Findings</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Conclusions</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(p => (
                  <tr key={p.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: 600 }}>#{p.id}</td>
                    <td style={{ padding: '1rem', fontWeight: 600, color: 'white', maxWidth: '380px' }}>
                      {p.question}
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                      {new Date(p.created_at).toLocaleDateString()}
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
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <button
                          onClick={() => {
                            onSelectProject(p.id);
                            setActiveTab(p.status === 'running' ? 'tracker' : 'results');
                          }}
                          className="btn btn-primary"
                          style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }}
                        >
                          <span>Open</span>
                          <ArrowRight size={12} />
                        </button>
                        <button
                          onClick={e => handleDelete(p.id, e)}
                          style={{ background: 'none', border: 'none', color: '#fb7185', cursor: 'pointer', padding: '0.3rem' }}
                          title="Delete Project"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
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
