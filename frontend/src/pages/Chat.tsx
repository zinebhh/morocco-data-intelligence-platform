import { useState } from 'react';
import { Send, Bot, User, Loader2, BookOpen } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { apiClient } from '../api/client';
import type { AskResponse } from '../api/client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: AskResponse['sources'];
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "👋 Bonjour ! Je suis votre assistant de recherche. Posez-moi une question sur les publications universitaires marocaines.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await apiClient.ask(input, 3);
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
        },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: '❌ Erreur lors de la génération de la réponse.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">🤖 Assistant IA</h2>
        <p className="text-gray-600 mt-1">Posez vos questions, l'IA répond à partir des publications indexées</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col" style={{ height: '600px' }}>
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center flex-shrink-0">
                  <Bot size={16} />
                </div>
              )}
              <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-first' : ''}`}>
                <div
                  className={`rounded-2xl px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  ) : (
                    msg.content
                  )}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <div className="text-xs font-semibold text-gray-500 flex items-center gap-1">
                      <BookOpen size={12} /> Sources :
                    </div>
                    {msg.sources.map((s, j) => (
                      <div key={j} className="text-xs bg-blue-50 border-l-2 border-primary-500 p-2 rounded">
                        <div className="font-medium text-gray-800">
                          [{j + 1}] {s.title} ({s.year})
                        </div>
                        <div className="text-gray-600 mt-1">{s.excerpt?.slice(0, 120)}...</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-300 text-gray-700 flex items-center justify-center flex-shrink-0">
                  <User size={16} />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center">
                <Bot size={16} />
              </div>
              <div className="bg-gray-100 rounded-2xl px-4 py-3 flex items-center gap-2 text-gray-500">
                <Loader2 className="animate-spin" size={14} />
                L'IA réfléchit...
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Posez votre question..."
              disabled={loading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </div>
          <div className="text-xs text-gray-500 mt-2">
            ⏱️ Les réponses peuvent prendre 1-2 min (LLM sur CPU)
          </div>
        </div>
      </div>
    </div>
  );
}