import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Prompt {
  id: number;
  prompt_text: string;
  category?: string;
  dataset_name?: string;
  created_at: string;
}

export interface ModelResponse {
  id: number;
  prompt_id: number;
  model_name: string;
  response_text: string;
  latency?: number;
  created_at: string;
}

export interface Evaluation {
  id: number;
  response_id: number;
  metric: string;
  score: number;
  evaluation_method: string;
  details?: string;
  created_at: string;
}

export interface Experiment {
  id: number;
  experiment_name: string;
  model_name: string;
  dataset_name: string;
  status: string;
  created_at: string;
}

export interface HumanFeedback {
  id: number;
  response_id: number;
  score: number;
  reviewer_name?: string;
  notes?: string;
  created_at: string;
}

export interface LeaderboardEntry {
  model_name: string;
  avg_score: number;
  response_count: number;
}

export const api = {
  prompts: {
    getAll: () => apiClient.get<Prompt[]>('/prompts/'),
    getById: (id: number) => apiClient.get<Prompt>(`/prompts/${id}`),
    create: (data: Partial<Prompt>) => apiClient.post<Prompt>('/prompts/', data),
    delete: (id: number) => apiClient.delete(`/prompts/${id}`),
  },
  
  responses: {
    getAll: (modelName?: string) => 
      apiClient.get<ModelResponse[]>('/responses/', { params: { model_name: modelName } }),
    getById: (id: number) => apiClient.get<ModelResponse>(`/responses/${id}`),
  },
  
  experiments: {
    getAll: () => apiClient.get<Experiment[]>('/experiments/'),
    getById: (id: number) => apiClient.get<Experiment>(`/experiments/${id}`),
    run: (data: Partial<Experiment>) => apiClient.post<Experiment>('/experiments/run', data),
    getSummary: (id: number) => apiClient.get(`/evaluation/experiment/${id}/summary`),
  },
  
  evaluation: {
    evaluateResponse: (responseId: number, method: string = 'rule') =>
      apiClient.post('/evaluation/evaluate-response', null, { params: { response_id: responseId, method } }),
    getLeaderboard: () => apiClient.get<LeaderboardEntry[]>('/evaluation/leaderboard'),
    getModelMetrics: (modelName: string) => apiClient.get(`/evaluation/metrics/${modelName}`),
  },
  
  humanFeedback: {
    getAll: () => apiClient.get<HumanFeedback[]>('/human-feedback/'),
    getForResponse: (responseId: number) => 
      apiClient.get<HumanFeedback[]>(`/human-feedback/response/${responseId}`),
    create: (data: Partial<HumanFeedback>) => 
      apiClient.post<HumanFeedback>('/human-feedback/', data),
  },
};

export default apiClient;
