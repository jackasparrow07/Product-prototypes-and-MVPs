import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from '@google/generative-ai';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(API_KEY);

const generationConfig = {
  temperature: 1,
  topP: 0.95,
  topK: 40,
  maxOutputTokens: 8192,
};

export async function processAudioWithGemini(audioBlob: Blob): Promise<string> {
  try {
    const model = genAI.getGenerativeModel({
      model: "gemini-1.5-flash-002",
      generationConfig,
    });

    // Convert audio blob to File object
    const file = new File([audioBlob], 'recording.ogg', { type: 'audio/ogg' });
    
    const chatSession = model.startChat({
      history: [
        {
          role: "user",
          parts: [
            {
              inlineData: {
                mimeType: file.type,
                data: await blobToBase64(file)
              },
            },
          ],
        },
      ],
    });

    const prompt = `Please analyze this recording and extract the following information. 
    Format your response as a valid JSON object with these keys:
    - actionItems: Array of specific tasks or actions mentioned
    - keyPoints: Array of main points or important information
    - nextSteps: Array of follow-up items or future actions
    
    Example format:
    {
      "actionItems": ["task 1", "task 2"],
      "keyPoints": ["point 1", "point 2"],
      "nextSteps": ["next step 1", "next step 2"]
    }`;

    const result = await chatSession.sendMessage(prompt);
    return result.response.text();
  } catch (error) {
    console.error('Error processing audio:', error);
    throw error;
  }
}

async function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result === 'string') {
        // Remove the data URL prefix
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      } else {
        reject(new Error('Failed to convert blob to base64'));
      }
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}