import React from 'react';
import { ModelResponse } from '../api/client';

interface ResponseViewerProps {
  response: ModelResponse;
  promptText?: string;
}

const ResponseViewer: React.FC<ResponseViewerProps> = ({ response, promptText }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg border border-slate-700">
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-slate-200">Response</h3>
          <span className="text-sm text-slate-400">
            Model: <span className="text-blue-400 font-medium">{response.model_name}</span>
          </span>
        </div>
        {response.latency && (
          <span className="text-xs text-slate-500">
            Latency: {response.latency.toFixed(2)}s
          </span>
        )}
      </div>

      {promptText && (
        <div className="mb-4 p-4 bg-slate-900 rounded border border-slate-700">
          <p className="text-xs text-slate-400 mb-1 uppercase font-semibold">Prompt</p>
          <p className="text-slate-300">{promptText}</p>
        </div>
      )}

      <div className="p-4 bg-slate-900 rounded border border-slate-700">
        <p className="text-xs text-slate-400 mb-1 uppercase font-semibold">Response</p>
        <p className="text-slate-200 whitespace-pre-wrap">{response.response_text}</p>
      </div>

      <div className="mt-4 text-xs text-slate-500">
        Generated: {new Date(response.created_at).toLocaleString()}
      </div>
    </div>
  );
};

export default ResponseViewer;
