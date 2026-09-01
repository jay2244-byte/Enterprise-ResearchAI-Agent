import React, { useEffect, useState } from 'react';
import { 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  Globe, 
  ExternalLink, 
  ShieldCheck, 
  HelpCircle,
  Clock,
  ArrowRight,
  Filter,
  Sparkles
} from 'lucide-react';
import { api } from '../api/client';
import TraceabilityModal from '../components/TraceabilityModal';
import SourceReliabilityModal from '../components/SourceReliabilityModal';
import ResearchQAWidget from '../components/ResearchQAWidget';

export default function ResultsPage({ projectId, setActiveTab }) {
  const [project, setProject] = useState(null);
  const [conclusions, setConclusions] = useState([]);
  const [findings, setFindings] = useState([]);
  const [sources, setSources] = useState([]);
  const [comparisons, setComparisons] = useState([]);
  const [contradictions, setContradictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modals & Filters
  const [selectedTraceConclusionId, setSelectedTraceConclusionId] = useState(null);
  const [selectedAuditSource, setSelectedAuditSource] = useState(null);
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('All');

  useEffect(() => {
    if (!projectId) return;

    setLoading(true);
    Promise.all([
      api.getProject(projectId),
      api.getConclusions(projectId),
      api.getFindings(projectId),
      api.getSources(projectId),
      api.getEvidenceComparison(projectId),
      api.getContradictions(projectId)
    ])
      .then(([p, c, f, s, comp, contra]) => {
        setProject(p);
        setConclusions(c);
        setFindings(f);
        setSources(s);
        setComparisons(comp);
        setContradictions(contra);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [projectId]);

  if (!projectId) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No research project selected.</div>;
  }

  if (loading) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>Synthesizing Traceable Research Results...</div>;
  }

  const categories = ['All', ...new Set(findings.map(f => f.category))];
  const filteredFindings = selectedCategoryFilter === 'All' ? findings : findings.filter(f => f.category === selectedCategoryFilter);

  return (
    <div className="page-wrapper">
      {/* Header Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9))', border: '1px solid rgba(59, 130, 246, 0.4)', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <span className="badge badge-completed">
            <CheckCircle2 size={12} /> Verified Traceable Results
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Created: {new Date(project.created_at).toLocaleString()}
          </span>
        </div>

        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'white', marginBottom: '0.75rem' }}>
          "{project.question}"
        </h1>

        {project.industry && (
          <div style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: 600, marginBottom: '1rem' }}>
            Industry Context: {project.industry} | Scope: {project.scope}
          </div>
        )}

        {/* Executive Summary */}
        <div style={{ background: 'var(--bg-primary)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent-blue)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Sparkles size={14} /> Executive Research Summary
          </div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
            {project.executive_summary || 'Analysis complete across retrieved empirical sources.'}
          </p>
        </div>
      </div>

      {/* 1. Major Conclusions (With Traceability Buttons) */}
      <div className="card">
        <div className="card-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={20} style={{ color: 'var(--accent-emerald)' }} />
            <span>Major Strategic Conclusions ({conclusions.length})</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Click "Why this conclusion?" for full evidence chain
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {conclusions.map((c, idx) => (
            <div 
              key={c.id} 
              style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.25rem' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span className={`badge badge-${c.confidence.toLowerCase()}`}>
                  {c.confidence} Confidence
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                  Rank #{c.rank_order} | Cites {c.supporting_findings_count} Findings
                </span>
              </div>

              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'white', marginBottom: '0.5rem' }}>
                {c.title}
              </h3>

              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem', lineHeight: '1.5' }}>
                {c.summary}
              </p>

              {/* Trace Action Button */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Reasoning: {c.reasoning_summary.slice(0, 100)}...
                </div>

                <button
                  onClick={() => setSelectedTraceConclusionId(c.id)}
                  className="btn btn-primary"
                  style={{ padding: '0.4rem 0.85rem', fontSize: '0.75rem' }}
                >
                  <HelpCircle size={14} />
                  <span>Why this conclusion? (View Evidence)</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Interactive Research Interrogation Q&A */}
      <ResearchQAWidget projectId={project.id} projectQuestion={project.question} />

      {/* 3. Contradictions & Contextual Tensions */}
      {contradictions.length > 0 && (
        <div className="card" style={{ border: '1px solid rgba(244, 63, 94, 0.4)' }}>
          <div className="card-title">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle size={20} style={{ color: 'var(--accent-rose)' }} />
              <span>Contradiction & Conflict Detection ({contradictions.length})</span>
            </div>
            <span style={{ fontSize: '0.75rem', color: '#fb7185' }}>
              Distinguishes true conflict from contextual differences
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {contradictions.map(contra => (
              <div key={contra.id} style={{ background: 'rgba(244, 63, 94, 0.05)', border: '1px solid rgba(244, 63, 94, 0.2)', borderRadius: '10px', padding: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span className="badge badge-low">
                    {contra.contradiction_type.replace('_', ' ').toUpperCase()}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Confidence: {contra.confidence}
                  </span>
                </div>

                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'white', marginBottom: '0.5rem' }}>
                  Topic: {contra.topic || 'Contextual Tension'}
                </h4>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.85rem' }}>
                  {contra.explanation}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', background: 'var(--bg-primary)', padding: '0.75rem', borderRadius: '8px', fontSize: '0.75rem' }}>
                  <div>
                    <div style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>Finding A ({contra.finding_a_source || 'Source A'}):</div>
                    <div style={{ color: 'white' }}>{contra.finding_a_title}</div>
                  </div>
                  <div>
                    <div style={{ color: 'var(--accent-amber)', fontWeight: 700 }}>Finding B ({contra.finding_b_source || 'Source B'}):</div>
                    <div style={{ color: 'white' }}>{contra.finding_b_title}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. Evidence Comparison Matrix */}
      {comparisons.length > 0 && (
        <div className="card">
          <div className="card-title">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={20} style={{ color: 'var(--accent-cyan)' }} />
              <span>Evidence Comparison & Perspective Synthesis</span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {comparisons.map(comp => (
              <div key={comp.id} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                    {comp.topic}
                  </span>
                  <span className="badge badge-medium">{comp.consensus_type}</span>
                </div>
                <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                  {comp.synthesis}
                </p>

                {comp.perspectives && comp.perspectives.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem' }}>
                    {comp.perspectives.map((p, pIdx) => (
                      <div key={pIdx} style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        • <strong style={{ color: 'white' }}>{p.source_title || 'Source'}:</strong> {p.viewpoint || p.perspective}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. Key Empirical Findings Explorer */}
      <div className="card">
        <div className="card-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={20} style={{ color: 'var(--accent-blue)' }} />
            <span>Structured Extracted Findings ({findings.length})</span>
          </div>

          {/* Category Filter Chips */}
          <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
            {categories.map((cat, cIdx) => (
              <button
                key={cIdx}
                onClick={() => setSelectedCategoryFilter(cat)}
                style={{
                  background: selectedCategoryFilter === cat ? 'var(--accent-blue)' : 'var(--bg-card)',
                  color: selectedCategoryFilter === cat ? 'white' : 'var(--text-secondary)',
                  border: '1px solid var(--border-color)',
                  padding: '0.25rem 0.6rem',
                  borderRadius: '9999px',
                  fontSize: '0.7rem',
                  cursor: 'pointer'
                }}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem' }}>
          {filteredFindings.map(f => {
            const evidenceQuote = f.evidence_items?.[0]?.quote_text || f.description;
            return (
              <div key={f.id} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span className="badge badge-medium">{f.category}</span>
                    <span className={`badge badge-${f.source_reliability_level?.toLowerCase() || 'medium'}`}>
                      {f.source_reliability_level || 'Medium'} Source
                    </span>
                  </div>

                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'white', marginBottom: '0.5rem' }}>
                    {f.title}
                  </h4>

                  <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                    {f.description}
                  </p>

                  <div style={{ background: 'var(--bg-primary)', padding: '0.65rem', borderRadius: '6px', borderLeft: '3px solid var(--accent-cyan)', fontSize: '0.75rem', fontStyle: 'italic', color: 'var(--text-muted)' }}>
                    "{evidenceQuote.slice(0, 180)}..."
                  </div>
                </div>

                <div style={{ marginTop: '1rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <span>{f.source_publisher || 'Web Reference'}</span>
                  {f.source_url && (
                    <a href={f.source_url} target="_blank" rel="noreferrer" style={{ color: 'var(--accent-blue)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                      <span>Source</span>
                      <ExternalLink size={10} />
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 6. Sources Collected & Reliability Scores */}
      <div className="card">
        <div className="card-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Globe size={20} style={{ color: 'var(--accent-purple)' }} />
            <span>Persisted Verified Sources ({sources.length})</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Click "Reliability Audit" to inspect calculation formula
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Source Title</th>
                <th style={{ padding: '0.75rem 1rem' }}>Publisher</th>
                <th style={{ padding: '0.75rem 1rem' }}>Type</th>
                <th style={{ padding: '0.75rem 1rem' }}>Reliability</th>
                <th style={{ padding: '0.75rem 1rem' }}>Relevance</th>
                <th style={{ padding: '0.75rem 1rem' }}>Audit</th>
              </tr>
            </thead>
            <tbody>
              {sources.map(s => (
                <tr key={s.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '1rem', fontWeight: 600, color: 'white', maxWidth: '350px' }}>
                    <a href={s.url} target="_blank" rel="noreferrer" style={{ color: 'white', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <span>{s.title}</span>
                      <ExternalLink size={12} style={{ color: 'var(--accent-blue)' }} />
                    </a>
                  </td>
                  <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{s.publisher}</td>
                  <td style={{ padding: '1rem' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>{s.source_type}</span>
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <span className={`badge badge-${s.reliability_level.toLowerCase()}`}>
                      {s.reliability_level} ({s.reliability_score}/100)
                    </span>
                  </td>
                  <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{s.relevance_score}</td>
                  <td style={{ padding: '1rem' }}>
                    <button
                      onClick={() => setSelectedAuditSource(s)}
                      className="btn btn-secondary"
                      style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }}
                    >
                      <span>Audit Score</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Traceability Modal */}
      {selectedTraceConclusionId && (
        <TraceabilityModal
          projectId={project.id}
          conclusionId={selectedTraceConclusionId}
          onClose={() => setSelectedTraceConclusionId(null)}
        />
      )}

      {/* Source Reliability Modal */}
      {selectedAuditSource && (
        <SourceReliabilityModal
          source={selectedAuditSource}
          onClose={() => setSelectedAuditSource(null)}
        />
      )}
    </div>
  );
}
