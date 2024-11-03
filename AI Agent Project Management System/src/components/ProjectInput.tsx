import React, { useState } from 'react';
import { Send, AlertCircle, Loader2 } from 'lucide-react';
import { useProjectStore } from '../store/projectStore';
import { GeminiService } from '../lib/ai';

export default function ProjectInput() {
  const [description, setDescription] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [isKeySet, setIsKeySet] = useState(false);
  const [validatingKey, setValidatingKey] = useState(false);
  const [keyError, setKeyError] = useState('');
  const { createProject, loading, error } = useProjectStore();

  const handleValidateKey = async () => {
    if (!apiKey) return;
    
    setValidatingKey(true);
    setKeyError('');
    
    try {
      const isValid = await GeminiService.validateApiKey(apiKey);
      if (isValid) {
        GeminiService.initialize(apiKey);
        setIsKeySet(true);
      } else {
        setKeyError('Invalid API key. Please check and try again.');
      }
    } catch (error) {
      setKeyError('Failed to validate API key. Please try again.');
    } finally {
      setValidatingKey(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description) return;
    await createProject(description);
    setDescription('');
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md flex items-center gap-2 text-red-700">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {!isKeySet ? (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Gemini API Key
          </label>
          <div className="flex gap-2">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="flex-1 px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your Gemini API key"
              disabled={validatingKey}
            />
            <button
              onClick={handleValidateKey}
              disabled={!apiKey || validatingKey}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 
                       disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {validatingKey ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Validating...</span>
                </>
              ) : (
                <span>Validate Key</span>
              )}
            </button>
          </div>
          {keyError && (
            <p className="mt-2 text-sm text-red-600">{keyError}</p>
          )}
        </div>
      ) : null}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Project Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 h-32"
            placeholder="Describe your project in detail..."
            disabled={loading || !isKeySet}
          />
        </div>
        
        <button
          type="submit"
          disabled={loading || !description || !isKeySet}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 
                   disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <span>Generate Project Plan</span>
              <Send size={18} />
            </>
          )}
        </button>
      </form>
    </div>
  );
}