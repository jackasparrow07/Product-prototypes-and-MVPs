export interface Agent {
  id: string;
  name: string;
  role: string;
  avatar: string;
  expertise: string[];
  status: 'idle' | 'working' | 'completed';
}

export interface Task {
  id: string;
  title: string;
  description: string;
  assignedTo: string;
  status: 'pending' | 'in-progress' | 'completed';
  dependencies: string[];
  output?: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  tasks: Task[];
  agents: Agent[];
  status: 'planning' | 'in-progress' | 'completed';
}