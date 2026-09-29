import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiClient } from '../api/client';
import type { Topic } from '../api/client';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Topics() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .topics()
      .then((data) => setTopics(data.topics))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-12 text-gray-500">⏳ Chargement...</div>;

  const pieData = topics.map((t) => ({ name: t.label, value: t.nb_publications }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">🏷️ Topics de recherche</h2>
        <p className="text-gray-600 mt-1">{topics.length} thématiques identifiées par LDA</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Répartition des publications</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-3">
          {topics.map((t, i) => (
            <div key={t.topic_id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div className="flex items-center gap-3 mb-2">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: COLORS[i % COLORS.length] }}
                />
                <h3 className="font-semibold text-gray-900">{t.label}</h3>
                <span className="ml-auto text-sm font-mono text-primary-600">
                  {t.nb_publications} pub.
                </span>
              </div>
              <p className="text-sm text-gray-600 italic">🔑 {t.keywords}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}