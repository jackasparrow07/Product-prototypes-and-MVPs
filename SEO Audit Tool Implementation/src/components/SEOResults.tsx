import React from 'react';
import { FileCheck, ArrowRight, CheckCircle2 } from 'lucide-react';
import type { SEOResult } from '../types/seo';

interface SEOResultsProps {
  results: SEOResult;
  onDownloadPDF: () => void;
  onViewDetails: () => void;
}

export const SEOResults: React.FC<SEOResultsProps> = ({
  results,
  onDownloadPDF,
  onViewDetails,
}) => (
  <div className="max-w-4xl mx-auto space-y-8">
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">SEO Score</h2>
        <span className="text-3xl font-bold text-indigo-600">{results.score}/100</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-4">
        <div
          className="bg-indigo-600 h-4 rounded-full transition-all duration-1000"
          style={{ width: `${results.score}%` }}
        ></div>
      </div>
    </div>

    <div className="bg-white rounded-2xl shadow-xl p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Recommendations</h2>
      <div className="space-y-4">
        {results.recommendations.slice(0, 4).map((rec) => (
          <div key={rec.id} className="flex items-start gap-3 p-4 bg-gray-50 rounded-xl">
            <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-gray-700 font-medium">{rec.title}</p>
              <p className="text-gray-500 text-sm mt-1">{rec.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>

    <div className="flex gap-4">
      <button
        onClick={onDownloadPDF}
        className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-4 px-6 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all"
      >
        <FileCheck className="w-5 h-5" />
        Download PDF Report
      </button>
      <button
        onClick={onViewDetails}
        className="flex-1 bg-white hover:bg-gray-50 text-gray-900 py-4 px-6 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all border border-gray-200"
      >
        View Detailed Analysis
        <ArrowRight className="w-5 h-5" />
      </button>
    </div>
  </div>
);