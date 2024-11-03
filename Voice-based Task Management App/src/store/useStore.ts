import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Recording, Task } from '../types';

interface State {
  recordings: Recording[];
  isRecording: boolean;
  currentAudioUrl: string | null;
  addRecording: (recording: Recording) => void;
  toggleTask: (recordingId: string, taskId: string) => void;
  setIsRecording: (isRecording: boolean) => void;
  setCurrentAudioUrl: (url: string | null) => void;
}

export const useStore = create<State>()(
  persist(
    (set) => ({
      recordings: [],
      isRecording: false,
      currentAudioUrl: null,
      addRecording: (recording) =>
        set((state) => ({
          recordings: [...state.recordings, recording],
        })),
      toggleTask: (recordingId, taskId) =>
        set((state) => ({
          recordings: state.recordings.map((recording) =>
            recording.id === recordingId
              ? {
                  ...recording,
                  tasks: recording.tasks.map((task) =>
                    task.id === taskId
                      ? { ...task, completed: !task.completed }
                      : task
                  ),
                }
              : recording
          ),
        })),
      setIsRecording: (isRecording) => set({ isRecording }),
      setCurrentAudioUrl: (url) => set({ currentAudioUrl: url }),
    }),
    {
      name: 'voice-tasks-storage',
    }
  )
);