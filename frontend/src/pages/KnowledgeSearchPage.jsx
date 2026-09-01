import React, { useState } from 'react';
import { Search, Database, ExternalLink, ArrowRight, Sparkles, FolderGit2, FileText, CheckCircle2, Globe } from 'lucide-react';
import { api } from '../api/client';

export default function KnowledgeSearchPage({ setActiveTab, onSelectProject }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const sampleSearchTerms = ['predictive maintenance', 'manufacturing', 'automation', 'risk', 'supply chain', 'ROI'];

  const handleSearch = (searchTerm) => {
    const q = searchTerm || query;
    if (!q.trim() || loading) return;

    setLoading(true);
    if (!searchTerm) setQuery(q);

    api.searchKnowledge(q)
      .then(data => {
        setResults(data);
        setLoading(false);
      })
      .catch(err => {
        alert(`Search failed: ${err.message}`);
        setLoading(false);
      });
  };

  const getItemIcon = (type) => {
    switch (type) {
      case 'project': return <FolderGit2 size={16} style={{ color: 'var(--accent-blue)' }} />;
      case 'finding': return <FileText size={16} style={{ color: 'var(--accent-emerald)' }} />;
      case 'conclusion': return <CheckCircle2 size={16} style={{ color: 'var(--accent-purple)' }} />;
      case 'source': return <Globe size={16} style={{ color: 'var(--accent-cyan)' }} />;
      default: return <Database size={16} />;
    }
  };

  return (
    <div className="page-wrapper">
      <div className="card" style={{ border: '1px solid rgba(59, 130, 246, 0.4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-cyan)', fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
          <Database size={16} /> Reusable Knowledge Base Engine
        </div>

        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'white', marginBottom: '0.5rem' }}>
          Search Cross-Project Research Repository
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          All past research projects, sources, findings, and conclusions remain permanently indexed and reusable across restarts.
        </p>

        <form onSubmit={e => { e.preventDefault(); handleSearch(); }} style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search concepts, e.g. 'predictive maintenance' or 'architecture'..."
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
          <button type="submit" disabled={loading || !query.trim()} className="btn btn-primary" style={{ padding: '0.85rem 1.5rem' }}>
            {loading ? <Sparkles size={18} className="spinner" /> : <Search size={18} />}
            <span>Search Repository</span>
          </button>
        </form>

        {/* Sample Terms */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Try searching:</span>
          {sampleSearchTerms.map((term, tIdx) => (
            <button
              key={tIdx}
              onClick={() => handleSearch(term)}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
                padding: '0.25rem 0.65rem',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              {term}
            </button>
          ))}
        </div>
      </div>

      {/* Search Results */}
      {results && (
        <div className="card">
          <div className="card-title">
            <span>Search Results for "{results.query}" ({results.total_results})</span>
          </div>

          {results.total_results === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
              No matches found in the knowledge base for "{results.query}". Try a different term or run a new research project.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {results.results.map((item, idx) => (
                <div key={idx} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '1.25rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {getItemIcon(item.type)}
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent-cyan)' }}>
                        {item.type}
                      </span>
                    </div>

                    <button
                      onClick={() => {
                        onSelectProject(item.project_id);
                        setActiveTab('results');
                      }}
                      className="btn btn-secondary"
                      style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
                    >
                      <span>Open Project Results</span>
                      <ArrowRight size={12} />
                    </button>
                  </div>

                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'white', marginBottom: '0.35rem' }}>
                    {item.title}
                  </h4>

                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                    {item.snippet}
                  </p>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)' }}>
                    <span>Project: {item.project_question}</span>
                    {item.url && (
                      <a href={item.url} target="_blank" rel="noreferrer" style={{ color: 'var(--accent-blue)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                        <span>URL Citation</span>
                        <ExternalLink size={10} />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
