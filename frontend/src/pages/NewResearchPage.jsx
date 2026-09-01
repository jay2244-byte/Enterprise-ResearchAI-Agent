import React, { useState } from 'react';
import { Play, Sparkles, SlidersHorizontal, HelpCircle } from 'lucide-react';
import { api } from '../api/client';

export default function NewResearchPage({ setActiveTab, onSelectProject }) {
  const [question, setQuestion] = useState('');
  const [industry, setIndustry] = useState('');
  const [scope, setScope] = useState('Comprehensive');
  const [maxSources, setMaxSources] = useState(8);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const sampleQuestions = [
    "How is AI transforming manufacturing operations?",
    "What AI technologies are changing retail supply chains?",
    "How is generative AI changing pharmaceutical research?",
    "What is the impact of agentic AI on enterprise cybersecurity?"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || submitting) return;

    setSubmitting(true);
    setError(null);

    try {
      const project = await api.createProject({
        question: question.trim(),
        industry: industry.trim() || undefined,
        scope: scope,
        max_sources: parseInt(maxSources, 10)
      });
      onSelectProject(project.id);
      setActiveTab('tracker');
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  return (
    <div className="page-wrapper" style={{ maxWidth: '900px' }}>
      <div className="card" style={{ border: '1px solid rgba(59, 130, 246, 0.4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-blue)', fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
          <Sparkles size={16} /> Autonomous Research Commissioning
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'white', marginBottom: '0.5rem' }}>
          Commission New Enterprise AI Research
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          The research agent will dynamically execute planning, multi-source retrieval, reliability scoring, evidence extraction, contradiction detection, and traceable conclusion synthesis.
        </p>

        {error && (
          <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#fb7185', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Main Question Input */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: 'white', marginBottom: '0.5rem' }}>
              Research Question <span style={{ color: 'var(--accent-rose)' }}>*</span>
            </label>
            <textarea
              rows={3}
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="e.g. How is AI transforming manufacturing operations?"
              required
              style={{
                width: '100%',
                background: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                padding: '1rem',
                color: 'white',
                fontSize: '1rem',
                outline: 'none',
                resize: 'vertical'
              }}
            />
          </div>

          {/* Sample Chips */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
              Or choose a sample evaluation prompt:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {sampleQuestions.map((sq, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setQuestion(sq)}
                  style={{
                    background: question === sq ? 'rgba(59, 130, 246, 0.2)' : 'var(--bg-card)',
                    border: `1px solid ${question === sq ? 'var(--accent-blue)' : 'var(--border-color)'}`,
                    color: question === sq ? 'white' : 'var(--text-secondary)',
                    padding: '0.4rem 0.85rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {sq}
                </button>
              ))}
            </div>
          </div>

          {/* Toggle Advanced */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--accent-cyan)',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              marginBottom: '1.5rem'
            }}
          >
            <SlidersHorizontal size={14} />
            <span>{showAdvanced ? 'Hide Optional Parameters' : 'Show Optional Parameters (Industry, Scope, Source Limits)'}</span>
          </button>

          {/* Advanced Fields */}
          {showAdvanced && (
            <div style={{ background: 'var(--bg-primary)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-color)', marginBottom: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                  Target Industry (Optional)
                </label>
                <input
                  type="text"
                  value={industry}
                  onChange={e => setIndustry(e.target.value)}
                  placeholder="e.g. Manufacturing, Retail, Pharma, Finance"
                  style={{
                    width: '100%',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '0.65rem 0.85rem',
                    color: 'white',
                    fontSize: '0.875rem'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                  Research Scope
                </label>
                <select
                  value={scope}
                  onChange={e => setScope(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '0.65rem 0.85rem',
                    color: 'white',
                    fontSize: '0.875rem'
                  }}
                >
                  <option value="Comprehensive">Comprehensive (Broad & Deep Analysis)</option>
                  <option value="Technical Focus">Technical Architecture Focus</option>
                  <option value="Business ROI Focus">Business ROI & Impact Focus</option>
                  <option value="Risk & Governance Focus">Risk & Regulatory Focus</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                  Max Web Sources to Retrieve: {maxSources}
                </label>
                <input
                  type="range"
                  min="4"
                  max="16"
                  value={maxSources}
                  onChange={e => setMaxSources(e.target.value)}
                  style={{ width: '100%', accentColor: 'var(--accent-blue)' }}
                />
              </div>
            </div>
          )}

          {/* Action Button */}
          <button
            type="submit"
            disabled={submitting || !question.trim()}
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.9rem', fontSize: '1rem' }}
          >
            {submitting ? (
              <>
                <Sparkles size={20} className="spinner" />
                <span>Launching Research Pipeline...</span>
              </>
            ) : (
              <>
                <Play size={20} />
                <span>Start Autonomous Research</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
