import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, ArrowRight, Terminal, RefreshCw } from 'lucide-react';
import { api } from '../api/client';

export default function LiveTrackerPage({ projectId, setActiveTab }) {
  const [progressData, setProgressData] = useState(null);
  const [project, setProject] = useState(null);
  const [error, setError] = useState(null);

  const STAGES = [
    "Research Planning",
    "Source Search",
    "Information Collection",
    "Source Storage",
    "Finding Extraction",
    "Evidence Comparison",
    "Contradiction Detection",
    "Conclusion Generation",
    "Completed"
  ];

  useEffect(() => {
    if (!projectId) return;

    // Load initial project details
    api.getProject(projectId).then(setProject).catch(err => setError(err.message));

    // Polling progress interval
    const interval = setInterval(() => {
      api.getProgress(projectId)
        .then(data => {
          setProgressData(data);
          if (data.status === 'completed') {
            clearInterval(interval);
          }
        })
        .catch(err => setError(err.message));
    }, 1500);

    return () => clearInterval(interval);
  }, [projectId]);

  if (!projectId) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No active research selected.</div>;
  }

  const currentStage = progressData?.current_stage || project?.current_stage || 'Queued';
  const progressPct = progressData?.progress_percentage || project?.progress_percentage || 0;
  const isCompleted = progressData?.status === 'completed' || project?.status === 'completed';
  const logs = progressData?.latest_run?.log_messages || [];

  const getStageStatus = (stageName) => {
    if (isCompleted) return 'completed';
    const currentIdx = STAGES.indexOf(currentStage);
    const stageIdx = STAGES.indexOf(stageName);

    if (stageIdx < currentIdx) return 'completed';
    if (stageIdx === currentIdx) return 'active';
    return 'pending';
  };

  return (
    <div className="page-wrapper" style={{ maxWidth: '1000px' }}>
      <div className="card" style={{ border: '1px solid rgba(59, 130, 246, 0.4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <span className={`badge badge-${isCompleted ? 'completed' : 'running'}`}>
              {isCompleted ? 'Completed' : 'Running Pipeline'}
            </span>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'white', marginTop: '0.25rem' }}>
              {project?.question || 'Live Research Execution Tracker'}
            </h2>
          </div>

          {isCompleted && (
            <button
              onClick={() => setActiveTab('results')}
              className="btn btn-primary"
            >
              <span>Explore Research Results</span>
              <ArrowRight size={16} />
            </button>
          )}
        </div>

        {/* Progress Bar */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
            <span>Stage: {currentStage}</span>
            <span>{progressPct}% Completed</span>
          </div>
          <div style={{ height: '8px', background: 'var(--bg-primary)', borderRadius: '4px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${progressPct}%`,
                background: 'linear-gradient(90deg, var(--accent-blue), var(--accent-cyan))',
                transition: 'width 0.4s ease'
              }}
            />
          </div>
        </div>

        {/* Live Stepper */}
        <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'white', marginBottom: '1rem' }}>
          Live Pipeline Workflow Stages
        </h4>

        <div className="stepper-container">
          {STAGES.slice(0, -1).map((stage, idx) => {
            const status = getStageStatus(stage);
            return (
              <div key={idx} className={`stepper-item ${status}`}>
                <div
                  className="step-icon"
                  style={{
                    background: status === 'completed' ? 'rgba(16, 185, 129, 0.2)' : status === 'active' ? 'rgba(59, 130, 246, 0.2)' : 'var(--bg-primary)',
                    color: status === 'completed' ? '#34d399' : status === 'active' ? '#60a5fa' : 'var(--text-muted)',
                    border: `1px solid ${status === 'completed' ? '#10b981' : status === 'active' ? '#3b82f6' : 'var(--border-color)'}`
                  }}
                >
                  {status === 'completed' ? (
                    <CheckCircle2 size={16} />
                  ) : status === 'active' ? (
                    <Loader2 size={16} className="spinner" />
                  ) : (
                    <span>{idx + 1}</span>
                  )}
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.875rem', fontWeight: 700, color: status === 'pending' ? 'var(--text-muted)' : 'white' }}>
                    {stage}
                  </div>
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {status === 'completed' ? '✓ Completed' : status === 'active' ? '→ In Progress' : '○ Pending'}
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Execution Console Logs */}
        <div style={{ marginTop: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            <Terminal size={14} /> Live Execution Audit Log ({logs.length} events)
          </div>

          <div style={{ background: '#090d14', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '1rem', fontFamily: 'JetBrains Mono, monospace', fontSize: '0.75rem', maxHeight: '220px', overflowY: 'auto' }}>
            {logs.length === 0 ? (
              <div style={{ color: 'var(--text-muted)' }}>Waiting for log events...</div>
            ) : (
              logs.map((log, lIdx) => (
                <div key={lIdx} style={{ marginBottom: '0.35rem', color: log.level === 'ERROR' ? '#fb7185' : '#94a3b8' }}>
                  <span style={{ color: 'var(--text-muted)' }}>[{new Date(log.timestamp).toLocaleTimeString()}]</span>{' '}
                  <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>[{log.stage}]</span>{' '}
                  {log.message}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
