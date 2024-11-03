import React from 'react';
import { useApiKeyStore } from './store/apiKeyStore';
import { useProjectStore } from './store/projectStore';
import ApiKeyInput from './components/ApiKeyInput';
import ProjectInput from './components/ProjectInput';
import AgentCard from './components/AgentCard';
import TaskList from './components/TaskList';
import ProjectHeader from './components/ProjectHeader';
import { Bot, ListTodo, Users } from 'lucide-react';

function App() {
  const { apiKey, setApiKey } = useApiKeyStore();
  const { project, updateTask, updateAgent } = useProjectStore();

  if (!apiKey) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <ApiKeyInput onValidKey={setApiKey} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bot className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">AI Agent Project System</h1>
            </div>
            <button
              onClick={() => setApiKey('')}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Change API Key
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {!project ? (
          <ProjectInput />
        ) : (
          <div className="space-y-8">
            <ProjectHeader project={project} />

            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Users className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-semibold text-gray-900">AI Agents</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {project.agents.map((agent) => (
                  <AgentCard key={agent.id} agent={agent} onUpdate={updateAgent} />
                ))}
              </div>
            </div>

            <div>
              <div className="flex items-center space-x-2 mb-4">
                <ListTodo className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-semibold text-gray-900">Tasks</h2>
              </div>
              <TaskList
                tasks={project.tasks}
                onTaskUpdate={updateTask}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;