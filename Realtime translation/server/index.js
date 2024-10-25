import express from 'express';
import { WebSocketServer } from 'ws';
import cors from 'cors';
import Groq from 'groq-sdk';
import { Readable } from 'stream';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const app = express();
app.use(cors());

// Initialize Groq with API key from environment variables
const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('New client connected');
  
  let audioChunks = [];
  
  ws.on('message', async (data) => {
    if (data instanceof Buffer) {
      audioChunks.push(data);
      
      // Convert audio chunks to readable stream
      const audioStream = new Readable();
      audioStream.push(Buffer.concat(audioChunks));
      audioStream.push(null);
      
      try {
        const transcription = await groq.audio.transcriptions.create({
          file: audioStream,
          model: "whisper-large-v3-turbo",
          language: "en", // Change based on source language
          response_format: "json"
        });
        
        ws.send(JSON.stringify({
          type: 'transcription',
          text: transcription.text
        }));
        
        // Clear chunks after processing
        audioChunks = [];
      } catch (error) {
        console.error('Transcription error:', error);
        ws.send(JSON.stringify({
          type: 'error',
          message: error.message
        }));
      }
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
