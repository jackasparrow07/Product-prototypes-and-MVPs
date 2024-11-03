import React from 'react';
import { Project } from '../types';
import StatusBadge from './StatusBadge';
import { Bot } from 'lucide-react';

interface ProjectHeaderProps {
  project: Project;
}

export default function ProjectHeader({ project }: ProjectHeaderProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <Bot className="w-8 h-8 text-blue-600" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{project.title}</h2>
            <p className="text-gray-600 mt-1">{project.description}</p>
          </div>
        </div>
        <StatusBadge status={project.status} />
      </div>
      
      <div className="mt-4 flex items-center space-x-4 text-sm text-gray-600">
        <div>
          <span className="font-medium">{project.agents.length}</span> Agents
        </div>
        <div>
          <span className="font-medium">
            {project.tasks.filter(t => t.status === 'completed').length}
          </span>
          /{project.tasks.length} Tasks Completed
        </div>
      </div>
    </div>
  );
}