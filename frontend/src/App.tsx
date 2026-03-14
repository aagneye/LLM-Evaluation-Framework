import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Experiments from './pages/Experiments';
import Prompts from './pages/Prompts';
import HumanEvaluation from './pages/HumanEvaluation';

const Navigation: React.FC = () => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  const linkClass = (path: string) => 
    `px-4 py-2 rounded-lg font-medium transition-colors ${
      isActive(path)
        ? 'bg-blue-600 text-white'
        : 'text-slate-300 hover:bg-slate-700 hover:text-white'
    }`;

  return (
    <nav className="bg-slate-800 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-white mr-8">LLM Eval Framework</h1>
            <div className="flex space-x-2">
              <Link to="/" className={linkClass('/')}>
                Dashboard
              </Link>
              <Link to="/experiments" className={linkClass('/experiments')}>
                Experiments
              </Link>
              <Link to="/prompts" className={linkClass('/prompts')}>
                Prompts
              </Link>
              <Link to="/human-eval" className={linkClass('/human-eval')}>
                Human Eval
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-slate-900">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/experiments" element={<Experiments />} />
            <Route path="/prompts" element={<Prompts />} />
            <Route path="/human-eval" element={<HumanEvaluation />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
