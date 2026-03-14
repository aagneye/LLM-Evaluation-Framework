import React from 'react';

interface ScoreCardProps {
  title: string;
  score: number;
  maxScore?: number;
  description?: string;
}

const ScoreCard: React.FC<ScoreCardProps> = ({ 
  title, 
  score, 
  maxScore = 10, 
  description 
}) => {
  const percentage = (score / maxScore) * 100;
  const getColor = (pct: number) => {
    if (pct >= 80) return 'text-green-400';
    if (pct >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg border border-slate-700">
      <h3 className="text-lg font-semibold text-slate-200 mb-2">{title}</h3>
      <div className="flex items-baseline gap-2 mb-2">
        <span className={`text-4xl font-bold ${getColor(percentage)}`}>
          {score.toFixed(1)}
        </span>
        <span className="text-slate-400 text-sm">/ {maxScore}</span>
      </div>
      {description && (
        <p className="text-slate-400 text-sm">{description}</p>
      )}
      <div className="mt-4 h-2 bg-slate-700 rounded-full overflow-hidden">
        <div 
          className={`h-full ${getColor(percentage).replace('text', 'bg')} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default ScoreCard;
