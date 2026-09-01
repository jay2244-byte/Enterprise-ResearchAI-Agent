import React, { useState } from 'react';
import { MessageSquare, Send, Sparkles, ExternalLink, ShieldCheck } from 'lucide-react';
import { api } from '../api/client';

export default function ResearchQAWidget({ projectId, projectQuestion }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sampleQuestions = [
    "Which areas have the strongest evidence for AI adoption?",
    "What are the biggest implementation risks identified?",
    "What core technologies are highlighted across the sources?"
  ];

  const handleAsk = async (questionToAsk) => {
    const qText = questionToAsk || query;
    if (!qText.trim() || loading) return;

    const userMsg = { role: 'user', content: qText };
    setMessages(prev => [...prev, userMsg]);
    if (!questionToAsk) setQuery('');
    setLoading(true);

    try {
      const res = await api.askProject(projectId, qText);
      const aiMsg = {
        role: 'assistant',
        content: res.answer,
        citations: res.citations || []
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error interrogating research database: ${err.message}`,
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ border: '1px solid rgba(59, 130, 246, 0.3)', background: 'linear-gradient(180deg, var(--bg-secondary), rgba(30, 41, 59, 0.4))' }}>
      <div className="card-title">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <MessageSquare size={20} style={{ color: 'var(--accent-blue)' }} />
          <span>Interrogate Project Research Knowledge</span>
        </div>
        <span className="badge badge-running">
          <ShieldCheck size={12} /> Strictly Grounded in Project Findings
        </span>
      </div>

      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
        Ask analytical questions about this specific research project. Answers are derived exclusively from stored evidence and verified sources.
      </p>

      {/* Suggested Chips */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
        {sampleQuestions.map((sq, idx) => (
          <button
            key={idx}
            onClick={() => handleAsk(sq)}
            disabled={loading}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-secondary)',
              padding: '0.35rem 0.75rem',
              borderRadius: '9999px',
              fontSize: '0.75rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            className="sample-chip"
          >
            {sq}
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      {messages.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.25rem', maxHeight: '400px', overflowY: 'auto', paddingRight: '0.5rem' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              <div
                style={{
                  maxWidth: '85%',
                  padding: '0.85rem 1.15rem',
                  borderRadius: msg.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                  background: msg.role === 'user' ? 'linear-gradient(135deg, var(--accent-blue), var(--accent-cyan))' : 'var(--bg-card)',
                  color: 'white',
                  fontSize: '0.875rem',
                  border: msg.role === 'user' ? 'none' : '1px solid var(--border-color)'
                }}
              >
                <div style={{ fontSize: '0.7rem', fontWeight: 700, opacity: 0.7, marginBottom: '0.25rem' }}>
                  {msg.role === 'user' ? 'Evaluator Query' : 'Grounded Research AI'}
                </div>
                <p style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</p>

                {/* Citations Footer */}
                {msg.citations && msg.citations.length > 0 && (
                  <div style={{ marginTop: '0.75rem', paddingTop: '0.65rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '0.35rem' }}>
                      Supporting Citations ({msg.citations.length}):
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      {msg.citations.map((c, cIdx) => (
                        <a
                          key={cIdx}
                          href={c.source_url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ fontSize: '0.75rem', color: '#93c5fd', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                        >
                          <ExternalLink size={10} />
                          <span>[{c.reliability_level}] {c.source_title}</span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Input Box */}
      <form onSubmit={e => { e.preventDefault(); handleAsk(); }} style={{ display: 'flex', gap: '0.75rem' }}>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ask something about this research..."
          disabled={loading}
          style={{
            flex: 1,
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            padding: '0.65rem 1rem',
            color: 'white',
            fontSize: '0.875rem',
            outline: 'none'
          }}
        />
        <button type="submit" disabled={loading || !query.trim()} className="btn btn-primary">
          {loading ? <Sparkles size={16} className="spinner" /> : <Send size={16} />}
          <span>Interrogate</span>
        </button>
      </form>
    </div>
  );
}
