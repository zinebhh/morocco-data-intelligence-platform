import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 600000,
});

// ============================================================
// TYPES (tous exportés avec "export interface")
// ============================================================

export interface Stats {
  total_publications: number;
  avg_topic_confidence: number | null;
  lda_coherence: number | null;
  publications_by_year: { year: number; count: number }[];
  publications_by_topic: { topic: string; count: number }[];
  models: { model_type: string; accuracy: number; f1_score: number }[];
}

export interface Topic {
  topic_id: number;
  label: string;
  keywords: string;
  nb_publications: number;
}

export interface Publication {
  openalex_id: string;
  title: string;
  publication_year: number;
  doi: string | null;
  main_topic: number;
  topic_probability: number;
  research_domain: string | null;
}

export interface SearchResult {
  score: number;
  title: string;
  text: string;
  main_topic: number;
  publication_year: number;
  chunk_type: string;
  openalex_id: string;
}

export interface AskResponse {
  question: string;
  answer: string;
  sources: {
    title: string;
    year: number;
    topic: number;
    score: number;
    excerpt: string;
  }[];
}

// ============================================================
// API CLIENT
// ============================================================

export const apiClient = {
  health: () => api.get('/health').then(r => r.data),
  stats: () => api.get<Stats>('/stats').then(r => r.data),
  topics: () => api.get<{ topics: Topic[] }>('/topics').then(r => r.data),
  publications: (
    page = 1,
    size = 20,
    filters?: { topic?: number; year_min?: number; year_max?: number }
  ) =>
    api.get('/publications', { params: { page, size, ...filters } }).then(r => r.data),
  search: (query: string, top_k = 5, mode: 'hybrid' | 'semantic' | 'keyword' = 'hybrid') =>
    api.post<{ results: SearchResult[] }>('/search', { query, top_k, mode }).then(r => r.data),
  ask: (question: string, top_k = 3) =>
    api.post<AskResponse>('/ask', { question, top_k }).then(r => r.data),
};