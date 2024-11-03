import React from 'react';
import { Agent } from '../types';
import StatusBadge from './StatusBadge';

interface AgentCardProps {
  agent: Agent;
  onUpdate: (agentId: string, updates: Partial<Agent>) => void;
}

export default function AgentCard({ agent, onUpdate }: AgentCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-center space-x-4">
        <img
          src={agent.avatar}
          alt={agent.name}
          className="w-12 h-12 rounded-full"
        />
        <div className="flex-1">
          <h3 className="font-semibold text-lg">{agent.name}</h3>
          <p className="text-gray-600 text-sm">{agent.role}</p>
        </div>
        <StatusBadge status={agent.status} />
      </div>
      
      <div className="mt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Expertise</h4>
        <div className="flex flex-wrap gap-2">
          {agent.expertise.map((skill, index) => (
            <span
              key={index}
              className="bg-gray-100 px-2 py-1 rounded-md text-xs text-gray-700"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}