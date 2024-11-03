import { GoogleGenerativeAI } from '@google/generative-ai';

export async function validateApiKey(apiKey: string): Promise<boolean> {
  try {
    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });
    
    // Send a simple test message to validate the API key
    const result = await model.generateContent("Test message for API validation");
    await result.response.text();
    return true;
  } catch (error) {
    console.error("API Key Validation Error:", error);
    return false;
  }
}

export function initializeGemini(apiKey: string) {
  const genAI = new GoogleGenerativeAI(apiKey);
  return genAI.getGenerativeModel({ 
    model: "gemini-1.5-pro",
    generationConfig: {
      temperature: 0.9,
      topP: 0.95,
      topK: 64,
      maxOutputTokens: 8192,
    }
  });
}