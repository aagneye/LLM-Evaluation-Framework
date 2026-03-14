import React, { useEffect, useState } from 'react';
import { api, Experiment } from '../api/client';
import PromptRunner from '../components/PromptRunner';

const Experiments: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExperiments();
  }, []);

  const loadExperiments = async () => {
    try {
      const response = await api.experiments.getAll();
      setExperiments(response.data);
    } catch (error) {
      console.error('Failed to load experiments:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-900/30 text-green-400';
      case 'running':
        return 'bg-blue-900/30 text-blue-400';
      case 'failed':
        return 'bg-red-900/30 text-red-400';
      default:
        return 'bg-slate-700 text-slate-400';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100 mb-2">Experiments</h1>
        <p className="text-slate-400">Manage and run evaluation experiments</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <PromptRunner />
        </div>

        <div className="lg:col-span-2">
          <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700">
            <div className="px-6 py-4 border-b border-slate-700">
              <h2 className="text-xl font-bold text-slate-200">Recent Experiments</h2>
            </div>

            {loading ? (
              <div className="p-6 text-slate-400">Loading experiments...</div>
            ) : experiments.length === 0 ? (
              <div className="p-6 text-slate-400">No experiments yet. Run your first experiment!</div>
            ) : (
              <div className="divide-y divide-slate-700">
                {experiments.map((exp) => (
                  <div key={exp.id} className="p-6 hover:bg-slate-700/30 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-slate-200 mb-1">
                          {exp.experiment_name}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-slate-400">
                          <span>Model: <span className="text-blue-400">{exp.model_name}</span></span>
                          <span>Dataset: <span className="text-purple-400">{exp.dataset_name}</span></span>
                        </div>
                        <div className="mt-2 text-xs text-slate-500">
                          {new Date(exp.created_at).toLocaleString()}
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(exp.status)}`}>
                        {exp.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Experiments;
