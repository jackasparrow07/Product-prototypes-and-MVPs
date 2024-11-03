import { GoogleGenerativeAI } from '@google/generative-ai';
import { Project } from '../types';

let model: any = null;

const generationConfig = {
  temperature: 0.9,
  topP: 0.8,
  topK: 40,
  maxOutputTokens: 8192,
};

export const validateApiKey = async (apiKey: string): Promise<boolean> => {
  try {
    const genAI = new GoogleGenerativeAI(apiKey);
    const tempModel = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
    const result = await tempModel.generateContent("Test message");
    await result.response.text();
    return true;
  } catch (error) {
    console.error('API Key Validation Error:', error);
    return false;
  }
};

export const initializeAI = (apiKey: string) => {
  const genAI = new GoogleGenerativeAI(apiKey);
  model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash",
    generationConfig,
  });
};

export const generateProjectPlan = async (description: string): Promise<string> => {
  if (!model) {
    throw new Error('AI not initialized. Please provide an API key first.');
  }

  const prompt = `
    As an AI project manager, create a detailed project plan based on this description: "${description}"
    
    Consider the following aspects:
    1. Break down the project into logical tasks
    2. Assign specialized AI agents with relevant expertise
    3. Define dependencies between tasks
    4. Set realistic status indicators
    
    Return ONLY a JSON object with this exact structure (no additional text or explanation):
    {
      "id": "unique-id",
      "title": "Extracted from description",
      "description": "Refined project description",
      "status": "planning",
      "agents": [
        {
          "id": "agent-id",
          "name": "Agent Name",
          "role": "Specific Role",
          "avatar": "https://ui-avatars.com/api/?name=Agent+Name&background=random",
          "expertise": ["skill1", "skill2"],
          "status": "idle"
        }
      ],
      "tasks": [
        {
          "id": "task-id",
          "title": "Task Name",
          "description": "Detailed task description",
          "assignedTo": "agent-id",
          "status": "pending",
          "dependencies": []
        }
      ]
    }`;

  try {
    const result = await model.generateContent(prompt);
    const response = await result.response.text();
    
    // Validate JSON structure
    const parsed = JSON.parse(response);
    if (!validateProjectStructure(parsed)) {
      throw new Error('Invalid project structure generated');
    }
    
    return response;
  } catch (error) {
    console.error('Project Generation Error:', error);
    throw new Error('Failed to generate project plan. Please try again with a more detailed description.');
  }
};

export const generateTaskUpdate = async (
  task: string,
  context: string
): Promise<string> => {
  if (!model) {
    throw new Error('AI not initialized');
  }

  const prompt = `
    As an AI agent working on this task: "${task}"
    With this context: "${context}"
    
    Provide a detailed update on the progress and any outputs generated.
    Keep the response concise but informative.
  `;

  try {
    const result = await model.generateContent(prompt);
    return result.response.text();
  } catch (error) {
    console.error('Task Update Error:', error);
    throw new Error('Failed to generate task update');
  }
};

export const getAgentResponse = async (
  role: string,
  expertise: string[],
  query: string
): Promise<string> => {
  if (!model) {
    throw new Error('AI not initialized');
  }

  const prompt = `
    As an AI agent with the role of "${role}"
    With expertise in: ${expertise.join(', ')}
    
    Respond to this query: "${query}"
    
    Provide a response that demonstrates your specific expertise and role.
  `;

  try {
    const result = await model.generateContent(prompt);
    return result.response.text();
  } catch (error) {
    console.error('Agent Response Error:', error);
    throw new Error('Failed to generate agent response');
  }
};

function validateProjectStructure(project: any): project is Project {
  if (!project || typeof project !== 'object') return false;
  
  const requiredFields = ['id', 'title', 'description', 'status', 'agents', 'tasks'];
  if (!requiredFields.every(field => field in project)) return false;
  
  if (!Array.isArray(project.agents) || !Array.isArray(project.tasks)) return false;
  
  // Validate agents
  for (const agent of project.agents) {
    if (!agent.id || !agent.name || !agent.role || !agent.avatar || 
        !Array.isArray(agent.expertise) || !agent.status) {
      return false;
    }
  }
  
  // Validate tasks
  for (const task of project.tasks) {
    if (!task.id || !task.title || !task.description || 
        !task.assignedTo || !task.status || !Array.isArray(task.dependencies)) {
      return false;
    }
  }
  
  return true;
}