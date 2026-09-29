import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid, Legend } from 'recharts';
import { apiClient } from '../api/client';
import type { Stats } from '../api/client';
import StatCard from '../components/StatCard';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    apiClient
      .stats()
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-12 text-gray-500">⏳ Chargement des statistiques...</div>;
  if (error) return <div className="text-center py-12 text-red-500">❌ Erreur : {error}</div>;
  if (!stats) return null;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">📊 Tableau de bord</h2>
        <p className="text-gray-600 mt-1">Vue d'ensemble des données NLP universitaires</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon="📚" label="Publications" value={stats.total_publications} />
        <StatCard icon="🎯" label="Confiance moyenne" value={stats.avg_topic_confidence?.toFixed(3) ?? 'N/A'} color="text-emerald-600" />
        <StatCard icon="🔬" label="Cohérence LDA" value={stats.lda_coherence?.toFixed(3) ?? 'N/A'} color="text-amber-600" />
        <StatCard icon="🤖" label="Modèles ML" value={stats.models.length} color="text-purple-600" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">📈 Publications par année</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={stats.publications_by_year}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">📊 Publications par topic</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={stats.publications_by_topic}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="topic" tick={{ fontSize: 11 }} angle={-15} textAnchor="end" height={70} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 lg:col-span-2">
          <h3 className="font-semibold text-gray-900 mb-4">🤖 Performance des modèles</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={stats.models}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model_type" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="accuracy" fill="#3b82f6" name="Accuracy" />
              <Bar dataKey="f1_score" fill="#f59e0b" name="F1" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}