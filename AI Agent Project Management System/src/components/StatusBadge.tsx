import React from 'react';
import { Brain, CheckCircle, Clock } from 'lucide-react';
import clsx from 'clsx';

interface StatusBadgeProps {
  status: 'idle' | 'working' | 'completed' | 'pending' | 'in-progress';
  size?: 'sm' | 'md';
}

export default function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const icons = {
    idle: Clock,
    working: Brain,
    completed: CheckCircle,
    pending: Clock,
    'in-progress': Brain,
  };

  const Icon = icons[status];

  return (
    <div
      className={clsx(
        'inline-flex items-center gap-2 rounded-full',
        {
          'px-3 py-1': size === 'md',
          'px-2 py-0.5 text-xs': size === 'sm',
          'bg-gray-100': status === 'idle' || status === 'pending',
          'bg-blue-100': status === 'working' || status === 'in-progress',
          'bg-green-100': status === 'completed'
        }
      )}
    >
      <Icon className={clsx('w-4 h-4', {
        'text-gray-500': status === 'idle' || status === 'pending',
        'text-blue-500 animate-pulse': status === 'working' || status === 'in-progress',
        'text-green-500': status === 'completed'
      })} />
      <span className="capitalize">{status}</span>
    </div>
  );
}