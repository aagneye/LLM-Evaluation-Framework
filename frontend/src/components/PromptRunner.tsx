import React, { useState } from 'react';
import { api } from '../api/client';

const PromptRunner: React.FC = () => {
  const [experimentName, setExperimentName] = useState('');
  const [modelName, setModelName] = useState('gpt-4o-mini');
  const [datasetName, setDatasetName] = useState('reasoning');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleRunExperiment = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await api.experiments.run({
        experiment_name: experimentName,
        model_name: modelName,
        dataset_name: datasetName,
      });

      setMessage(`Experiment started successfully! ID: ${response.data.id}`);
      setExperimentName('');
    } catch (error) {
      setMessage('Failed to start experiment. Please try again.');
      console.error('Error running experiment:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg border border-slate-700">
      <h2 className="text-xl font-bold text-slate-200 mb-4">Run New Experiment</h2>
      
      <form onSubmit={handleRunExperiment} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Experiment Name
          </label>
          <input
            type="text"
            value={experimentName}
            onChange={(e) => setExperimentName(e.target.value)}
            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="My Experiment"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Model
          </label>
          <select
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="gpt-4o-mini">GPT-4o Mini</option>
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            <option value="llama3">Llama 3 (Local)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Dataset
          </label>
          <select
            value={datasetName}
            onChange={(e) => setDatasetName(e.target.value)}
            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="reasoning">Reasoning</option>
            <option value="safety">Safety</option>
            <option value="qa">Q&A</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-medium rounded transition-colors"
        >
          {loading ? 'Starting...' : 'Run Experiment'}
        </button>
      </form>

      {message && (
        <div className={`mt-4 p-3 rounded ${message.includes('success') ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default PromptRunner;
