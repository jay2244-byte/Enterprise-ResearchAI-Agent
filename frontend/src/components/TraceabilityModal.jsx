import React, { useEffect, useState } from 'react';
import { X, ArrowDown, ExternalLink, ShieldAlert, ShieldCheck, FileText, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';

export default function TraceabilityModal({ projectId, conclusionId, onClose }) {
  const [traceData, setTraceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (projectId && conclusionId) {
      setLoading(true);
      api.getConclusionTrace(projectId, conclusionId)
        .then(data => {
          setTraceData(data);
          setLoading(false);
        })
        .catch(err => {
          setError(err.message);
          setLoading(false);
        });
    }
  }, [projectId, conclusionId]);

  if (!conclusionId) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
          <div>
            <span className="badge badge-high" style={{ marginBottom: '0.25rem' }}>
              <CheckCircle2 size={12} /> Traceable Lineage Engine
            </span>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white' }}>
              Why This Conclusion? (Evidence Traceability)
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted)' }}>
            Loading evidence lineage...
          </div>
        )}

        {error && (
          <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.1)', color: '#fb7185', borderRadius: '8px' }}>
            Failed to load trace: {error}
          </div>
        )}

        {traceData && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Step 1: Conclusion Node */}
            <div style={{ background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(6, 182, 212, 0.05))', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '12px', padding: '1.25rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent-cyan)', marginBottom: '0.25rem' }}>
                Stage 1: Derived Conclusion
              </div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'white', marginBottom: '0.5rem' }}>
                {traceData.conclusion_title}
              </h4>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                {traceData.reasoning_summary}
              </p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <ArrowDown size={24} style={{ color: 'var(--accent-blue)' }} />
            </div>

            {/* Step 2: Supporting Findings */}
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span>Stage 2: Supporting Empirical Findings ({traceData.supporting_findings.length})</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>{traceData.unique_sources_count} Verified Sources</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {traceData.supporting_findings.map((item, idx) => (
                  <div key={idx} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span className="badge badge-medium">{item.category}</span>
                      <span className={`badge badge-${item.source_reliability_level.toLowerCase()}`}>
                        {item.source_reliability_level} Reliability ({item.source_reliability_score}/100)
                      </span>
                    </div>

                    <h5 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'white', marginBottom: '0.5rem' }}>
                      {item.title}
                    </h5>

                    {/* Step 3: Verbatim Evidence Quotes */}
                    <div style={{ background: 'var(--bg-secondary)', borderLeft: '3px solid var(--accent-blue)', padding: '0.75rem 1rem', borderRadius: '0 8px 8px 0', margin: '0.75rem 0' }}>
                      <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                        Stage 3: Verbatim Evidence Quote
                      </div>
                      <p style={{ fontSize: '0.825rem', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                        "{item.evidence_quotes[0] || 'Direct quote retrieved from source content.'}"
                      </p>
                    </div>

                    {/* Step 4: Original Source Citation */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <div>
                        <strong>Publisher:</strong> {item.source_publisher} — {item.source_title}
                      </div>
                      {item.source_url && (
                        <a 
                          href={item.source_url} 
                          target="_blank" 
                          rel="noreferrer"
                          style={{ color: 'var(--accent-blue)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.25rem', fontWeight: 600 }}
                        >
                          <span>View Original Source</span>
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
