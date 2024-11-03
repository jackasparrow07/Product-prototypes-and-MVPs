import React, { useState } from 'react';
import { validateApiKey } from '../utils/gemini';
import { Key, Loader } from 'lucide-react';

interface ApiKeyInputProps {
  onValidKey: (key: string) => void;
}

export default function ApiKeyInput({ onValidKey }: ApiKeyInputProps) {
  const [apiKey, setApiKey] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsValidating(true);
    setError(null);

    try {
      const isValid = await validateApiKey(apiKey);
      if (isValid) {
        onValidKey(apiKey);
      } else {
        setError('Invalid API key. Please check your key and try again.');
      }
    } catch (err) {
      setError('An error occurred while validating the API key.');
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-3 mb-4">
        <Key className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">Enter Gemini API Key</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
            API Key
          </label>
          <input
            type="password"
            id="apiKey"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter your Gemini API key"
            required
          />
        </div>

        {error && (
          <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isValidating || !apiKey}
          className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isValidating ? (
            <>
              <Loader className="w-4 h-4 mr-2 animate-spin" />
              Validating...
            </>
          ) : (
            'Validate API Key'
          )}
        </button>
      </form>

      <p className="mt-4 text-xs text-gray-500">
        Your API key is stored locally and never sent to our servers. 
        Need a key? Visit the{' '}
        <a 
          href="https://ai.google.dev/tutorials/setup" 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800"
        >
          Google AI Studio
        </a>
      </p>
    </div>
  );
}