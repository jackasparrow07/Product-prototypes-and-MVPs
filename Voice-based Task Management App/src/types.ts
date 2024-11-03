export interface Task {
  id: string;
  text: string;
  completed: boolean;
  category: 'action' | 'key-point' | 'next-step';
}

export interface Recording {
  id: string;
  audioUrl: string;
  transcript: string;
  tasks: Task[];
  timestamp: number;
}