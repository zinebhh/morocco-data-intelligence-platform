import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import type { Publication } from '../api/client';

export default function Publications() {
  const [publications, setPublications] = useState<Publication[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterTopic, setFilterTopic] = useState<number | ''>('');
  const [filterYear, setFilterYear] = useState<number | ''>('');

  const size = 10;

  useEffect(() => {
    setLoading(true);
    apiClient
      .publications(page, size, {
        topic: filterTopic === '' ? undefined : filterTopic,
        year_min: filterYear === '' ? undefined : filterYear,
      })
      .then((data) => {
        setPublications(data.items);
        setTotal(data.total);
      })
      .finally(() => setLoading(false));
  }, [page, filterTopic, filterYear]);

  const totalPages = Math.ceil(total / size);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">📚 Publications</h2>
        <p className="text-gray-600 mt-1">{total} publications indexées</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 flex flex-wrap gap-4">
        <select
          value={filterTopic}
          onChange={(e) => {
            setFilterTopic(e.target.value === '' ? '' : Number(e.target.value));
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 rounded-lg"
        >
          <option value="">Tous les topics</option>
          {[0, 1, 2, 3, 4].map((t) => (
            <option key={t} value={t}>Topic {t}</option>
          ))}
        </select>
        <select
          value={filterYear}
          onChange={(e) => {
            setFilterYear(e.target.value === '' ? '' : Number(e.target.value));
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 rounded-lg"
        >
          <option value="">Toutes les années</option>
          {[2020, 2021, 2022, 2023, 2024, 2025, 2026].map((y) => (
            <option key={y} value={y}>Depuis {y}</option>
          ))}
        </select>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">⏳ Chargement...</div>}

      {!loading && (
        <div className="space-y-3">
          {publications.map((p) => (
            <div key={p.openalex_id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-900">{p.title}</h3>
              <div className="flex flex-wrap gap-3 text-sm text-gray-500 mt-2">
                <span>📅 {p.publication_year || 'N/A'}</span>
                <span>🎯 Topic {p.main_topic}</span>
                <span>📊 Confiance: {(p.topic_probability * 100).toFixed(1)}%</span>
                {p.research_domain && <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">{p.research_domain}</span>}
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg disabled:opacity-50"
          >
            ← Précédent
          </button>
          <span className="px-4 py-2 bg-primary-600 text-white rounded-lg">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg disabled:opacity-50"
          >
            Suivant →
          </button>
        </div>
      )}
    </div>
  );
}