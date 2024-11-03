import React from 'react';
import { Task } from '../types';
import StatusBadge from './StatusBadge';
import { ChevronDown, ChevronUp } from 'lucide-react';
import clsx from 'clsx';

interface TaskListProps {
  tasks: Task[];
  onTaskUpdate: (taskId: string, updates: Partial<Task>) => void;
}

export default function TaskList({ tasks, onTaskUpdate }: TaskListProps) {
  const [expandedTasks, setExpandedTasks] = React.useState<Set<string>>(new Set());

  const toggleTask = (taskId: string) => {
    setExpandedTasks(prev => {
      const next = new Set(prev);
      if (next.has(taskId)) {
        next.delete(taskId);
      } else {
        next.add(taskId);
      }
      return next;
    });
  };

  return (
    <div className="space-y-4">
      {tasks.map((task) => {
        const isExpanded = expandedTasks.has(task.id);
        
        return (
          <div
            key={task.id}
            className={clsx(
              'bg-white rounded-lg shadow-sm p-4 border-l-4',
              {
                'border-gray-300': task.status === 'pending',
                'border-blue-400': task.status === 'in-progress',
                'border-green-400': task.status === 'completed'
              }
            )}
          >
            <div className="flex items-start gap-4">
              <button
                onClick={() => {
                  const nextStatus = {
                    pending: 'in-progress',
                    'in-progress': 'completed',
                    completed: 'pending'
                  }[task.status];
                  onTaskUpdate(task.id, { status: nextStatus as Task['status'] });
                }}
                className="mt-1"
              >
                <StatusBadge status={task.status} size="sm" />
              </button>
              
              <div className="flex-1">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{task.title}</h3>
                    <p className="text-gray-600 text-sm mt-1">
                      {isExpanded ? task.description : task.description.slice(0, 100) + '...'}
                    </p>
                  </div>
                  <button
                    onClick={() => toggleTask(task.id)}
                    className="ml-2 p-1 hover:bg-gray-100 rounded-full"
                  >
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-gray-500" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-500" />
                    )}
                  </button>
                </div>
                
                {isExpanded && (
                  <>
                    {task.output && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-md">
                        <h4 className="text-sm font-medium text-gray-700 mb-1">Output:</h4>
                        <p className="text-sm text-gray-600">{task.output}</p>
                      </div>
                    )}
                    
                    {task.dependencies.length > 0 && (
                      <div className="mt-3">
                        <h4 className="text-xs font-medium text-gray-500">Dependencies:</h4>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {task.dependencies.map((dep) => (
                            <span
                              key={dep}
                              className="text-xs bg-gray-100 px-2 py-1 rounded"
                            >
                              {dep}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
              
              <div className="text-sm text-gray-500">
                Assigned to: {task.assignedTo}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}