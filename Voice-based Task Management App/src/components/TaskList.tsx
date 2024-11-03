import React from 'react';
import { CheckSquare, Square, PlayCircle } from 'lucide-react';
import { useStore } from '../store/useStore';

export function TaskList() {
  const { recordings, toggleTask } = useStore();

  const categoryIcons = {
    action: '🎯',
    'key-point': '💡',
    'next-step': '➡️',
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-8">
      {recordings.map((recording) => (
        <div
          key={recording.id}
          className="bg-white rounded-lg shadow-md p-6 space-y-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <audio
                src={recording.audioUrl}
                controls
                className="w-64"
              />
              <span className="text-sm text-gray-500">
                {new Date(recording.timestamp).toLocaleString()}
              </span>
            </div>
          </div>

          <div className="space-y-6">
            {['action', 'key-point', 'next-step'].map((category) => {
              const categoryTasks = recording.tasks.filter(
                (task) => task.category === category
              );

              if (categoryTasks.length === 0) return null;

              return (
                <div key={category} className="space-y-2">
                  <h3 className="text-lg font-semibold capitalize flex items-center gap-2">
                    {categoryIcons[category as keyof typeof categoryIcons]}{' '}
                    {category.replace('-', ' ')}s
                  </h3>
                  <div className="space-y-2">
                    {categoryTasks.map((task) => (
                      <div
                        key={task.id}
                        className="flex items-start space-x-3 p-2 hover:bg-gray-50 rounded-lg transition-colors"
                      >
                        <button
                          onClick={() => toggleTask(recording.id, task.id)}
                          className="mt-0.5"
                        >
                          {task.completed ? (
                            <CheckSquare className="w-5 h-5 text-green-500" />
                          ) : (
                            <Square className="w-5 h-5 text-gray-400" />
                          )}
                        </button>
                        <span
                          className={`flex-1 ${
                            task.completed ? 'line-through text-gray-400' : ''
                          }`}
                        >
                          {task.text}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}