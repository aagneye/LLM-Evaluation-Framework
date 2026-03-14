import React, { useEffect, useState } from 'react';
import { api, ModelResponse, Prompt } from '../api/client';
import ResponseViewer from '../components/ResponseViewer';

const HumanEvaluation: React.FC = () => {
  const [responses, setResponses] = useState<ModelResponse[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentPrompt, setCurrentPrompt] = useState<Prompt | null>(null);
  const [score, setScore] = useState(5);
  const [reviewerName, setReviewerName] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitMessage, setSubmitMessage] = useState('');

  useEffect(() => {
    loadResponses();
  }, []);

  useEffect(() => {
    if (responses.length > 0 && currentIndex < responses.length) {
      loadPromptForResponse(responses[currentIndex]);
    }
  }, [currentIndex, responses]);

  const loadResponses = async () => {
    try {
      const response = await api.responses.getAll();
      setResponses(response.data);
    } catch (error) {
      console.error('Failed to load responses:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPromptForResponse = async (response: ModelResponse) => {
    try {
      const promptRes = await api.prompts.getById(response.prompt_id);
      setCurrentPrompt(promptRes.data);
    } catch (error) {
      console.error('Failed to load prompt:', error);
    }
  };

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitMessage('');

    try {
      await api.humanFeedback.create({
        response_id: responses[currentIndex].id,
        score,
        reviewer_name: reviewerName || undefined,
        notes: notes || undefined,
      });

      setSubmitMessage('Feedback submitted successfully!');
      setScore(5);
      setNotes('');
      
      setTimeout(() => {
        if (currentIndex < responses.length - 1) {
          setCurrentIndex(currentIndex + 1);
          setSubmitMessage('');
        }
      }, 1000);
    } catch (error) {
      setSubmitMessage('Failed to submit feedback. Please try again.');
      console.error('Failed to submit feedback:', error);
    }
  };

  if (loading) {
    return <div className="text-slate-400">Loading responses...</div>;
  }

  if (responses.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400">No responses available for evaluation.</p>
      </div>
    );
  }

  const currentResponse = responses[currentIndex];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100 mb-2">Human Evaluation</h1>
        <p className="text-slate-400">
          Review and score model responses ({currentIndex + 1} of {responses.length})
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ResponseViewer 
            response={currentResponse} 
            promptText={currentPrompt?.prompt_text}
          />
        </div>

        <div className="lg:col-span-1">
          <div className="bg-slate-800 rounded-lg p-6 shadow-lg border border-slate-700">
            <h2 className="text-xl font-bold text-slate-200 mb-4">Submit Feedback</h2>
            
            <form onSubmit={handleSubmitFeedback} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Score (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={score}
                  onChange={(e) => setScore(Number(e.target.value))}
                  className="w-full"
                />
                <div className="text-center text-3xl font-bold text-blue-400 mt-2">
                  {score}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Reviewer Name (optional)
                </label>
                <input
                  type="text"
                  value={reviewerName}
                  onChange={(e) => setReviewerName(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Notes (optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  placeholder="Additional feedback..."
                />
              </div>

              <button
                type="submit"
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition-colors"
              >
                Submit Feedback
              </button>
            </form>

            {submitMessage && (
              <div className={`mt-4 p-3 rounded ${submitMessage.includes('success') ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                {submitMessage}
              </div>
            )}

            <div className="mt-6 flex gap-2">
              <button
                onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
                disabled={currentIndex === 0}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-slate-200 font-medium rounded transition-colors"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentIndex(Math.min(responses.length - 1, currentIndex + 1))}
                disabled={currentIndex === responses.length - 1}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-slate-200 font-medium rounded transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HumanEvaluation;
