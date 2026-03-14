import React, { useEffect, useState } from 'react';
import { api, Prompt } from '../api/client';

const Prompts: React.FC = () => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newPrompt, setNewPrompt] = useState({
    prompt_text: '',
    category: '',
    dataset_name: '',
  });

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    try {
      const response = await api.prompts.getAll();
      setPrompts(response.data);
    } catch (error) {
      console.error('Failed to load prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.prompts.create(newPrompt);
      setNewPrompt({ prompt_text: '', category: '', dataset_name: '' });
      setShowAddForm(false);
      loadPrompts();
    } catch (error) {
      console.error('Failed to add prompt:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Prompts</h1>
          <p className="text-slate-400">Manage evaluation prompts and datasets</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition-colors"
        >
          {showAddForm ? 'Cancel' : 'Add Prompt'}
        </button>
      </div>

      {showAddForm && (
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg border border-slate-700">
          <h2 className="text-xl font-bold text-slate-200 mb-4">Add New Prompt</h2>
          <form onSubmit={handleAddPrompt} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Prompt Text
              </label>
              <textarea
                value={newPrompt.prompt_text}
                onChange={(e) => setNewPrompt({ ...newPrompt, prompt_text: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Category
                </label>
                <input
                  type="text"
                  value={newPrompt.category}
                  onChange={(e) => setNewPrompt({ ...newPrompt, category: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Dataset Name
                </label>
                <input
                  type="text"
                  value={newPrompt.dataset_name}
                  onChange={(e) => setNewPrompt({ ...newPrompt, dataset_name: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <button
              type="submit"
              className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition-colors"
            >
              Add Prompt
            </button>
          </form>
        </div>
      )}

      <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700">
        {loading ? (
          <div className="p-6 text-slate-400">Loading prompts...</div>
        ) : prompts.length === 0 ? (
          <div className="p-6 text-slate-400">No prompts yet. Add your first prompt!</div>
        ) : (
          <div className="divide-y divide-slate-700">
            {prompts.map((prompt) => (
              <div key={prompt.id} className="p-6 hover:bg-slate-700/30 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-slate-200 mb-2">{prompt.prompt_text}</p>
                    <div className="flex items-center gap-4 text-sm">
                      {prompt.category && (
                        <span className="px-2 py-1 bg-blue-900/30 text-blue-400 rounded text-xs">
                          {prompt.category}
                        </span>
                      )}
                      {prompt.dataset_name && (
                        <span className="px-2 py-1 bg-purple-900/30 text-purple-400 rounded text-xs">
                          {prompt.dataset_name}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Prompts;
