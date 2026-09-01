const API_BASE = '/api';

export async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // System Stats
  getStats: () => fetchJson('/system/stats'),
  getHealth: () => fetchJson('/system/health'),

  // Research Projects
  createProject: (data) => fetchJson('/research', { method: 'POST', body: JSON.stringify(data) }),
  listProjects: (skip = 0, limit = 20, status = null) => {
    let url = `/research?skip=${skip}&limit=${limit}`;
    if (status) url += `&status=${status}`;
    return fetchJson(url);
  },
  getProject: (id) => fetchJson(`/research/${id}`),
  runProject: (id) => fetchJson(`/research/${id}/run`, { method: 'POST' }),
  getProgress: (id) => fetchJson(`/research/${id}/progress`),
  getSources: (id) => fetchJson(`/research/${id}/sources`),
  getFindings: (id, category = null) => {
    let url = `/research/${id}/findings`;
    if (category) url += `?category=${encodeURIComponent(category)}`;
    return fetchJson(url);
  },
  getEvidenceComparison: (id) => fetchJson(`/research/${id}/evidence-comparison`),
  getContradictions: (id) => fetchJson(`/research/${id}/contradictions`),
  getConclusions: (id) => fetchJson(`/research/${id}/conclusions`),
  getConclusionTrace: (id, conclusionId) => fetchJson(`/research/${id}/trace/${conclusionId}`),
  askProject: (id, question) => fetchJson(`/research/${id}/ask`, { method: 'POST', body: JSON.stringify({ question }) }),
  deleteProject: (id) => fetchJson(`/research/${id}`, { method: 'DELETE' }),

  // Knowledge Base Search
  searchKnowledge: (query) => fetchJson(`/knowledge/search?q=${encodeURIComponent(query)}`)
};
