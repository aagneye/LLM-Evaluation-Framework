import React, { useEffect, useState } from 'react';
import ScoreCard from '../components/ScoreCard';
import Leaderboard from '../components/Leaderboard';
import MetricsChart from '../components/MetricsChart';
import { api } from '../api/client';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    totalExperiments: 0,
    totalResponses: 0,
    avgScore: 0,
  });
  const [metricsData, setMetricsData] = useState<any[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [experimentsRes, responsesRes, leaderboardRes] = await Promise.all([
        api.experiments.getAll(),
        api.responses.getAll(),
        api.evaluation.getLeaderboard(),
      ]);

      setStats({
        totalExperiments: experimentsRes.data.length,
        totalResponses: responsesRes.data.length,
        avgScore: leaderboardRes.data.length > 0 
          ? leaderboardRes.data.reduce((sum, entry) => sum + entry.avg_score, 0) / leaderboardRes.data.length
          : 0,
      });

      const sampleMetrics = [
        { metric: 'correctness', avg_score: 7.5 },
        { metric: 'reasoning', avg_score: 8.2 },
        { metric: 'helpfulness', avg_score: 7.8 },
        { metric: 'safety', avg_score: 9.1 },
      ];
      setMetricsData(sampleMetrics);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100 mb-2">Dashboard</h1>
        <p className="text-slate-400">Overview of LLM evaluation metrics and experiments</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ScoreCard 
          title="Total Experiments" 
          score={stats.totalExperiments} 
          maxScore={100}
          description="Completed evaluation runs"
        />
        <ScoreCard 
          title="Total Responses" 
          score={stats.totalResponses} 
          maxScore={1000}
          description="Model responses evaluated"
        />
        <ScoreCard 
          title="Average Score" 
          score={stats.avgScore} 
          maxScore={10}
          description="Across all models"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsChart data={metricsData} />
        <Leaderboard />
      </div>
    </div>
  );
};

export default Dashboard;
