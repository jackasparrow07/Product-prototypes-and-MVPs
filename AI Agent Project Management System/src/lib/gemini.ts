import { GoogleGenerativeAI } from '@google/generative-ai';

// Configuration for the Gemini model
const MODEL_CONFIG = {
  temperature: 0.9,
  topP: 0.8,
  topK: 40,
  maxOutputTokens: 8192,
};

let model: any = null;

export const initializeGemini = (apiKey: string) => {
  const genAI = new GoogleGenerativeAI(apiKey);
  model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash",
    generationConfig: MODEL_CONFIG,
  });
  return model;
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

export const generateContent = async (prompt: string): Promise<string> => {
  if (!model) {
    throw new Error('Gemini model not initialized. Please call initializeGemini first.');
  }

  try {
    const result = await model.generateContent(prompt);
    return result.response.text();
  } catch (error) {
    console.error('Content Generation Error:', error);
    throw new Error('Failed to generate content');
  }
};

export const generateStructuredContent = async <T>(
  prompt: string,
  validator: (data: any) => data is T
): Promise<T> => {
  if (!model) {
    throw new Error('Gemini model not initialized. Please call initializeGemini first.');
  }

  try {
    const result = await model.generateContent(prompt);
    const content = await result.response.text();
    const parsedContent = JSON.parse(content);
    
    if (!validator(parsedContent)) {
      throw new Error('Generated content does not match expected structure');
    }
    
    return parsedContent;
  } catch (error) {
    console.error('Structured Content Generation Error:', error);
    throw new Error('Failed to generate structured content');
  }
};