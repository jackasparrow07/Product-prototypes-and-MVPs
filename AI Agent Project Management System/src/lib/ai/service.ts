import { GoogleGenerativeAI } from '@google/generative-ai';
import type { AIService, AIServiceConfig } from './types';
import { MODEL_NAME, GENERATION_CONFIG } from './config';

export class GeminiService implements AIService {
  private model: any;
  private static instance: GeminiService | null = null;

  private constructor(apiKey: string, config: AIServiceConfig = { model: MODEL_NAME, generationConfig: GENERATION_CONFIG }) {
    const genAI = new GoogleGenerativeAI(apiKey);
    this.model = genAI.getGenerativeModel(config);
  }

  static initialize(apiKey: string): GeminiService {
    if (!GeminiService.instance) {
      GeminiService.instance = new GeminiService(apiKey);
    }
    return GeminiService.instance;
  }

  static getInstance(): GeminiService {
    if (!GeminiService.instance) {
      throw new Error('GeminiService not initialized. Call initialize first.');
    }
    return GeminiService.instance;
  }

  static async validateApiKey(apiKey: string): Promise<boolean> {
    try {
      const genAI = new GoogleGenerativeAI(apiKey);
      const model = genAI.getGenerativeModel({ model: MODEL_NAME });
      const result = await model.generateContent("Test message");
      await result.response.text();
      return true;
    } catch (error) {
      console.error('API Key Validation Error:', error);
      return false;
    }
  }

  async generateContent(prompt: string): Promise<string> {
    try {
      const result = await this.model.generateContent(prompt);
      return result.response.text();
    } catch (error) {
      console.error('Content Generation Error:', error);
      throw new Error('Failed to generate content');
    }
  }

  async generateStructuredContent<T>(prompt: string, validator: (data: unknown) => T): Promise<T> {
    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response.text();
      const parsed = JSON.parse(response);
      return validator(parsed);
    } catch (error) {
      console.error('Structured Content Generation Error:', error);
      throw new Error('Failed to generate structured content');
    }
  }
}