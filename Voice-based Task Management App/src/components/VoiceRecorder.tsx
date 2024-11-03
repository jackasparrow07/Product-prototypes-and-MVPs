import React, { useRef, useState, useEffect } from 'react';
import { Mic, Square, Loader, MicOff, Volume2 } from 'lucide-react';
import { useStore } from '../store/useStore';
import { processAudioWithGemini } from '../services/gemini';

export function VoiceRecorder() {
  const { setIsRecording, addRecording } = useStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [deviceInfo, setDeviceInfo] = useState<MediaDeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [recordingDuration, setRecordingDuration] = useState<number>(0);
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const audioContext = useRef<AudioContext | null>(null);
  const analyzer = useRef<AnalyserNode | null>(null);
  const animationFrame = useRef<number>();
  const startTime = useRef<number>(0);
  const durationInterval = useRef<number>();

  useEffect(() => {
    // Check initial permission status
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(() => setHasPermission(true))
      .catch(() => setHasPermission(false));

    // List available audio devices
    navigator.mediaDevices.enumerateDevices()
      .then(devices => {
        const audioDevices = devices.filter(device => device.kind === 'audioinput');
        setDeviceInfo(audioDevices);
        if (audioDevices.length > 0) {
          setSelectedDevice(audioDevices[0].deviceId);
        }
      });

    return () => {
      if (animationFrame.current) {
        cancelAnimationFrame(animationFrame.current);
      }
      if (durationInterval.current) {
        clearInterval(durationInterval.current);
      }
    };
  }, []);

  const updateAudioLevel = () => {
    if (analyzer.current) {
      const dataArray = new Uint8Array(analyzer.current.frequencyBinCount);
      analyzer.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setAudioLevel(average);
      animationFrame.current = requestAnimationFrame(updateAudioLevel);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: selectedDevice ? { exact: selectedDevice } : undefined
        }
      });

      // Set up audio analysis
      audioContext.current = new AudioContext();
      const source = audioContext.current.createMediaStreamSource(stream);
      analyzer.current = audioContext.current.createAnalyser();
      analyzer.current.fftSize = 256;
      source.connect(analyzer.current);
      
      mediaRecorder.current = new MediaRecorder(stream);
      chunks.current = [];
      startTime.current = Date.now();

      // Start duration counter
      durationInterval.current = window.setInterval(() => {
        setRecordingDuration(Math.floor((Date.now() - startTime.current) / 1000));
      }, 1000);

      mediaRecorder.current.ondataavailable = (e) => {
        chunks.current.push(e.data);
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(chunks.current, { type: 'audio/mp3' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        setIsProcessing(true);
        try {
          const geminiResponse = await processAudioWithGemini(audioBlob);
          const parsedResponse = JSON.parse(geminiResponse);
          
          const newRecording = {
            id: Date.now().toString(),
            audioUrl,
            transcript: '',
            tasks: [
              ...parsedResponse.actionItems.map((text: string) => ({
                id: crypto.randomUUID(),
                text,
                completed: false,
                category: 'action' as const,
              })),
              ...parsedResponse.keyPoints.map((text: string) => ({
                id: crypto.randomUUID(),
                text,
                completed: false,
                category: 'key-point' as const,
              })),
              ...parsedResponse.nextSteps.map((text: string) => ({
                id: crypto.randomUUID(),
                text,
                completed: false,
                category: 'next-step' as const,
              })),
            ],
            timestamp: Date.now(),
          };
          
          addRecording(newRecording);
        } catch (error) {
          console.error('Error processing recording:', error);
        } finally {
          setIsProcessing(false);
          setRecordingDuration(0);
        }
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      updateAudioLevel();
    } catch (error) {
      console.error('Error starting recording:', error);
      setHasPermission(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);

      if (animationFrame.current) {
        cancelAnimationFrame(animationFrame.current);
      }
      if (durationInterval.current) {
        clearInterval(durationInterval.current);
      }
      if (audioContext.current) {
        audioContext.current.close();
      }
    }
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2">
      <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
        {/* Permission Status */}
        <div className="flex items-center justify-center space-x-2">
          {hasPermission === null ? (
            <span className="text-gray-500">Checking mic access...</span>
          ) : hasPermission ? (
            <div className="flex items-center text-green-500">
              <Mic className="w-4 h-4 mr-2" />
              <span>Microphone access granted</span>
            </div>
          ) : (
            <div className="flex items-center text-red-500">
              <MicOff className="w-4 h-4 mr-2" />
              <span>Microphone access denied</span>
            </div>
          )}
        </div>

        {/* Device Selection */}
        {deviceInfo.length > 0 && (
          <select
            value={selectedDevice}
            onChange={(e) => setSelectedDevice(e.target.value)}
            className="w-full p-2 border rounded-md"
            disabled={mediaRecorder.current?.state === 'recording'}
          >
            {deviceInfo.map((device) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `Microphone ${device.deviceId.slice(0, 5)}...`}
              </option>
            ))}
          </select>
        )}

        {/* Recording Status */}
        {mediaRecorder.current?.state === 'recording' && (
          <div className="flex items-center justify-center space-x-4">
            <div className="flex items-center">
              <Volume2 className="w-4 h-4 mr-2 text-blue-500" />
              <div className="w-32 h-2 bg-gray-200 rounded-full">
                <div
                  className="h-full bg-blue-500 rounded-full transition-all duration-100"
                  style={{ width: `${(audioLevel / 255) * 100}%` }}
                />
              </div>
            </div>
            <span className="text-blue-500 font-mono">
              {formatDuration(recordingDuration)}
            </span>
          </div>
        )}

        {/* Record Button */}
        <div className="flex justify-center">
          {isProcessing ? (
            <div className="animate-spin">
              <Loader className="w-12 h-12 text-blue-500" />
            </div>
          ) : (
            <button
              onClick={mediaRecorder.current?.state === 'recording' ? stopRecording : startRecording}
              disabled={!hasPermission || isProcessing}
              className={`rounded-full p-4 transition-colors ${
                !hasPermission
                  ? 'bg-gray-300 cursor-not-allowed'
                  : mediaRecorder.current?.state === 'recording'
                  ? 'bg-red-500 hover:bg-red-600'
                  : 'bg-blue-500 hover:bg-blue-600'
              }`}
            >
              {mediaRecorder.current?.state === 'recording' ? (
                <Square className="w-8 h-8 text-white" />
              ) : (
                <Mic className="w-8 h-8 text-white" />
              )}
            </button>
          )}
        </div>

        {/* Processing Status */}
        {isProcessing && (
          <div className="text-center text-sm text-gray-500">
            Processing your recording...
          </div>
        )}
      </div>
    </div>
  );
}