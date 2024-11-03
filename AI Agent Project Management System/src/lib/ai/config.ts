export const MODEL_NAME = "gemini-1.5-pro";

export const GENERATION_CONFIG = {
  temperature: 0.9,
  topP: 0.8,
  topK: 40,
  maxOutputTokens: 8192,
} as const;

export const PROMPTS = {
  PROJECT_PLAN: (description: string) => `
    As an AI project manager, create a detailed project plan based on this description: "${description}"
    
    Consider the following aspects:
    1. Break down the project into logical tasks
    2. Assign specialized AI agents with relevant expertise
    3. Define dependencies between tasks
    4. Set realistic status indicators
    
    Return ONLY a JSON object with this exact structure:
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
          "avatar": "https://ui-avatars.com/api/?name=Agent+Name",
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
          "dependencies": ["dependent-task-id"]
        }
      ]
    }
  `,
  
  TASK_UPDATE: (task: string, context: string) => `
    As an AI agent working on this task: "${task}"
    With this context: "${context}"
    
    Provide a detailed update on the progress and any outputs generated.
    Keep the response concise but informative.
  `,
  
  AGENT_RESPONSE: (role: string, expertise: string[], query: string) => `
    As an AI agent with the role of "${role}"
    With expertise in: ${expertise.join(', ')}
    
    Respond to this query: "${query}"
    
    Provide a response that demonstrates your specific expertise and role.
  `,
} as const;