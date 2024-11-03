import React from 'react';
import { X, AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';
import type { SEOResult, Metric } from '../types/seo';

interface DetailedAnalysisProps {
  results: SEOResult;
  onClose: () => void;
}

const StatusIcon = ({ status }: { status: Metric['status'] }) => {
  switch (status) {
    case 'good':
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    case 'warning':
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    case 'error':
      return <AlertCircle className="w-5 h-5 text-red-500" />;
  }
};

export const DetailedAnalysis: React.FC<DetailedAnalysisProps> = ({
  results,
  onClose,
}) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto m-4">
      <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Detailed SEO Analysis</h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      </div>
      
      <div className="p-6 space-y-8">
        {/* Score Section */}
        <section>
          <h3 className="text-xl font-semibold mb-4">Overall Score: {results.score}/100</h3>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-indigo-600 h-4 rounded-full transition-all duration-1000"
              style={{ width: `${results.score}%` }}
            />
          </div>
        </section>

        {/* Metrics Section */}
        <section>
          <h3 className="text-xl font-semibold mb-4">Key Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {results.metrics.map((metric) => (
              <div
                key={metric.name}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-xl"
              >
                <div className="flex items-center gap-3">
                  <StatusIcon status={metric.status} />
                  <span className="font-medium">{metric.name}</span>
                </div>
                <span className="text-gray-700">{metric.value}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Recommendations Section */}
        <section>
          <h3 className="text-xl font-semibold mb-4">All Recommendations</h3>
          <div className="space-y-4">
            {results.recommendations.map((rec) => (
              <div
                key={rec.id}
                className="p-4 bg-gray-50 rounded-xl space-y-2"
              >
                <div className="flex items-center gap-2">
                  <span className={`
                    px-2 py-1 text-xs font-medium rounded-full
                    ${rec.priority === 'high' ? 'bg-red-100 text-red-700' :
                      rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'}
                  `}>
                    {rec.priority.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-500 capitalize">{rec.category}</span>
                </div>
                <h4 className="font-semibold text-gray-900">{rec.title}</h4>
                <p className="text-gray-600">{rec.description}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  </div>
);