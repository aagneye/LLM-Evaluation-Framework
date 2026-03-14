import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface MetricData {
  metric: string;
  avg_score: number;
}

interface MetricsChartProps {
  data: MetricData[];
}

const MetricsChart: React.FC<MetricsChartProps> = ({ data }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg border border-slate-700">
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Metrics Breakdown</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
          <XAxis 
            dataKey="metric" 
            stroke="#94a3b8"
            tick={{ fill: '#94a3b8' }}
          />
          <YAxis 
            stroke="#94a3b8"
            tick={{ fill: '#94a3b8' }}
            domain={[0, 10]}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1e293b', 
              border: '1px solid #475569',
              borderRadius: '0.5rem'
            }}
            labelStyle={{ color: '#e2e8f0' }}
          />
          <Legend wrapperStyle={{ color: '#94a3b8' }} />
          <Bar dataKey="avg_score" fill="#3b82f6" name="Average Score" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MetricsChart;
