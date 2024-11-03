import React from 'react';
import { VoiceRecorder } from './components/VoiceRecorder';
import { TaskList } from './components/TaskList';
import { Brain } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-3">
            <Brain className="w-8 h-8 text-blue-500" />
            <h1 className="text-2xl font-bold text-gray-900">Voice Task Manager</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <TaskList />
        <VoiceRecorder />
      </main>
    </div>
  );
}

export default App;