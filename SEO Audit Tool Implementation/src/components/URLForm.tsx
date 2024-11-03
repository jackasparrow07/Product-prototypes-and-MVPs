import React from 'react';
import { Search, Download, BarChart3, Loader2 } from 'lucide-react';

interface URLFormProps {
  url: string;
  isAnalyzing: boolean;
  isBackingUp: boolean;
  onUrlChange: (url: string) => void;
  onAnalyze: (e: React.FormEvent) => void;
  onBackup: () => void;
}

export const URLForm: React.FC<URLFormProps> = ({
  url,
  isAnalyzing,
  isBackingUp,
  onUrlChange,
  onAnalyze,
  onBackup,
}) => (
  <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-xl p-8 mb-12">
    <form onSubmit={onAnalyze} className="space-y-6">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <input
          type="url"
          placeholder="Enter website URL (e.g., https://example.com)"
          value={url}
          onChange={(e) => onUrlChange(e.target.value)}
          className="w-full pl-12 pr-4 py-4 rounded-xl border border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
          required
        />
      </div>
      <div className="flex gap-4">
        <button
          type="submit"
          disabled={isAnalyzing || isBackingUp}
          className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-4 px-6 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50"
        >
          {isAnalyzing ? (
            <Loader2 className="animate-spin" />
          ) : (
            <>
              <BarChart3 className="w-5 h-5" />
              Analyze SEO
            </>
          )}
        </button>
        <button
          type="button"
          disabled={isAnalyzing || isBackingUp}
          onClick={onBackup}
          className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-4 px-6 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50"
        >
          {isBackingUp ? (
            <Loader2 className="animate-spin" />
          ) : (
            <>
              <Download className="w-5 h-5" />
              Backup Page
            </>
          )}
        </button>
      </div>
    </form>
  </div>
);