import type { GoogleGenerativeAI, GenerativeModel } from '@google/generative-ai';

export interface AIService {
  generateContent(prompt: string): Promise<string>;
  generateStructuredContent<T>(prompt: string, validator: (data: unknown) => T): Promise<T>;
}

export interface AIServiceConfig {
  model: string;
  generationConfig: {
    temperature: number;
    topP: number;
    topK: number;
    maxOutputTokens: number;
  };
}