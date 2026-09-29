import { Outlet, NavLink } from 'react-router-dom';
import { Home, Search, MessageSquare, BookOpen, Tag } from 'lucide-react';

export default function Layout() {
  const navItems = [
    { to: '/', label: 'Accueil', icon: Home },
    { to: '/search', label: 'Recherche', icon: Search },
    { to: '/chat', label: 'Assistant IA', icon: MessageSquare },
    { to: '/publications', label: 'Publications', icon: BookOpen },
    { to: '/topics', label: 'Topics', icon: Tag },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🎓</span>
              <h1 className="text-xl font-bold text-primary-700">EduData</h1>
            </div>
            <div className="flex gap-1">
              {navItems.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition ${
                      isActive
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`
                  }
                >
                  <Icon size={16} />
                  <span className="hidden sm:inline">{label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      <footer className="text-center text-sm text-gray-500 py-8">
        EduData © 2026 — Plateforme de recherche universitaire
      </footer>
    </div>
  );
}