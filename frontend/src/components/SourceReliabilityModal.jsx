import React from 'react';
import { X, ShieldCheck, Award, FileText, Calendar, Target } from 'lucide-react';

export default function SourceReliabilityModal({ source, onClose }) {
  if (!source) return null;

  const breakdown = source.reliability_breakdown || {};
  const levelClass = source.reliability_level === 'High' ? 'badge-high' : source.reliability_level === 'Medium' ? 'badge-medium' : 'badge-low';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
          <div>
            <span className={`badge ${levelClass}`} style={{ marginBottom: '0.25rem' }}>
              <ShieldCheck size={12} /> Rule-Based Reliability Evaluation
            </span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'white' }}>
              Source Reliability Audit: {source.publisher || 'Web Publisher'}
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        <div style={{ marginBottom: '1.5rem', background: 'var(--bg-card)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'white', marginBottom: '0.25rem' }}>
            {source.title}
          </h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', wordBreak: 'break-all' }}>
            {source.url}
          </p>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Score</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)' }}>{source.reliability_score} / 100</div>
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Classification</div>
              <span className={`badge ${levelClass}`}>{source.reliability_level} Trust</span>
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Source Type</div>
              <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>{source.source_type}</span>
            </div>
          </div>
        </div>

        <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'white', marginBottom: '1rem' }}>
          Deterministic Calculation Breakdown (Non-LLM Rule Formula)
        </h4>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          {/* Factor 1: Domain Authority */}
          <div style={{ background: 'var(--bg-card)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', fontWeight: 700, color: 'white' }}>
                <Award size={16} style={{ color: 'var(--accent-blue)' }} />
                <span>Domain Authority</span>
              </div>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                {breakdown.domain_authority?.score || 0} / {breakdown.domain_authority?.max || 35} pts
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              {breakdown.domain_authority?.rationale || 'Evaluates institutional TLD (.edu, .gov), analyst reputation, or enterprise authority.'}
            </p>
          </div>

          {/* Factor 2: Content Depth */}
          <div style={{ background: 'var(--bg-card)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', fontWeight: 700, color: 'white' }}>
                <FileText size={16} style={{ color: 'var(--accent-emerald)' }} />
                <span>Content Depth & Substance</span>
              </div>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                {breakdown.content_depth?.score || 0} / {breakdown.content_depth?.max || 25} pts
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              {breakdown.content_depth?.rationale || 'Evaluates word count density and empirical text length.'}
            </p>
          </div>

          {/* Factor 3: Recency */}
          <div style={{ background: 'var(--bg-card)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', fontWeight: 700, color: 'white' }}>
                <Calendar size={16} style={{ color: 'var(--accent-amber)' }} />
                <span>Recency & Validity</span>
              </div>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                {breakdown.recency?.score || 0} / {breakdown.recency?.max || 20} pts
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              {breakdown.recency?.rationale || 'Assesses publication year and freshness of reported data.'}
            </p>
          </div>

          {/* Factor 4: Relevance */}
          <div style={{ background: 'var(--bg-card)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', fontWeight: 700, color: 'white' }}>
                <Target size={16} style={{ color: 'var(--accent-purple)' }} />
                <span>Topical Relevance</span>
              </div>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                {breakdown.topical_relevance?.score || 0} / {breakdown.topical_relevance?.max || 20} pts
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              {breakdown.topical_relevance?.rationale || 'Measures keyword match ratio against sub-question parameters.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
