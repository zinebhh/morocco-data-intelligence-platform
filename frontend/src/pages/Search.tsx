import { useState } from 'react';
import { Search as SearchIcon, Loader2 } from 'lucide-react';
import { apiClient } from '../api/client';
import type { SearchResult } from '../api/client';

export default function Search() {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<'hybrid' | 'semantic' | 'keyword'>('hybrid');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const data = await apiClient.search(query, 10, mode);
      setResults(data.results);
    } catch (e) {
      console.error(e);
      alert('Erreur de recherche');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">🔍 Recherche sémantique</h2>
        <p className="text-gray-600 mt-1">Trouvez des publications par le sens, pas seulement par mots-clés</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <SearchIcon size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Ex: artificial intelligence in education"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as any)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="hybrid">Hybride (BM25 + vecteurs)</option>
            <option value="semantic">Sémantique (vecteurs)</option>
            <option value="keyword">Mots-clés (BM25)</option>
          </select>
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <SearchIcon size={18} />}
            Rechercher
          </button>
        </div>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">🔎 Recherche en cours...</div>}

      {!loading && searched && results.length === 0 && (
        <div className="text-center py-8 text-gray-500">Aucun résultat trouvé</div>
      )}

      <div className="space-y-4">
        {results.map((r, i) => (
          <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition">
            <div className="flex items-start justify-between gap-4">
              <h3 className="font-semibold text-gray-900 text-lg">{r.title}</h3>
              <span className="flex-shrink-0 px-3 py-1 bg-primary-100 text-primary-700 text-xs font-mono rounded-full">
                {(r.score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex gap-3 text-sm text-gray-500 mt-2">
              <span>📅 {r.publication_year || 'N/A'}</span>
              <span>🎯 Topic {r.main_topic}</span>
              <span>📄 {r.chunk_type}</span>
            </div>
            <p className="mt-3 text-gray-700 leading-relaxed">{r.text.slice(0, 300)}...</p>
          </div>
        ))}
      </div>
    </div>
  );
}