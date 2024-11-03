import { create } from 'zustand';
import type { Project, Task, Agent } from '../types';
import { GeminiService, PROMPTS } from '../lib/ai';
import { validateProjectStructure } from '../lib/ai/validators';

interface ProjectState {
  project: Project | null;
  loading: boolean;
  error: string | null;
  createProject: (description: string) => Promise<void>;
  updateTask: (taskId: string, updates: Partial<Task>) => Promise<void>;
  updateAgent: (agentId: string, updates: Partial<Agent>) => void;
  getAgentInput: (agentId: string, query: string) => Promise<string>;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  project: null,
  loading: false,
  error: null,

  createProject: async (description: string) => {
    set({ loading: true, error: null });
    try {
      const aiService = GeminiService.getInstance();
      const projectData = await aiService.generateStructuredContent(
        PROMPTS.PROJECT_PLAN(description),
        validateProjectStructure
      );
      set({ project: projectData, loading: false });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to create project plan', 
        loading: false 
      });
    }
  },

  updateTask: async (taskId: string, updates: Partial<Task>) => {
    const state = get();
    if (!state.project) return;

    try {
      set({ loading: true });
      
      const task = state.project.tasks.find(t => t.id === taskId);
      if (!task) throw new Error('Task not found');

      if (updates.status === 'completed') {
        const aiService = GeminiService.getInstance();
        const output = await aiService.generateContent(
          PROMPTS.TASK_UPDATE(task.description, JSON.stringify(state.project))
        );
        updates.output = output;
      }

      const updatedTasks = state.project.tasks.map(t =>
        t.id === taskId ? { ...t, ...updates } : t
      );

      set({
        project: {
          ...state.project,
          tasks: updatedTasks
        },
        loading: false
      });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to update task',
        loading: false 
      });
    }
  },

  updateAgent: (agentId: string, updates: Partial<Agent>) => {
    set((state) => {
      if (!state.project) return state;
      
      const updatedAgents = state.project.agents.map(agent =>
        agent.id === agentId ? { ...agent, ...updates } : agent
      );

      return {
        project: {
          ...state.project,
          agents: updatedAgents
        }
      };
    });
  },

  getAgentInput: async (agentId: string, query: string) => {
    const state = get();
    if (!state.project) throw new Error('No active project');

    const agent = state.project.agents.find(a => a.id === agentId);
    if (!agent) throw new Error('Agent not found');

    const aiService = GeminiService.getInstance();
    return aiService.generateContent(
      PROMPTS.AGENT_RESPONSE(agent.role, agent.expertise, query)
    );
  },
}));