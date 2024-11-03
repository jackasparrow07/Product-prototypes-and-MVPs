import type { Project } from '../../types';

export function validateProjectStructure(data: unknown): Project {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid project data structure');
  }

  const project = data as any;

  if (!project.id || !project.title || !project.description || 
      !Array.isArray(project.agents) || !Array.isArray(project.tasks)) {
    throw new Error('Missing required project fields');
  }

  // Validate agents
  project.agents.forEach((agent: any) => {
    if (!agent.id || !agent.name || !agent.role || !Array.isArray(agent.expertise)) {
      throw new Error('Invalid agent structure');
    }
  });

  // Validate tasks
  project.tasks.forEach((task: any) => {
    if (!task.id || !task.title || !task.description || !task.assignedTo || !Array.isArray(task.dependencies)) {
      throw new Error('Invalid task structure');
    }
  });

  return project as Project;
}