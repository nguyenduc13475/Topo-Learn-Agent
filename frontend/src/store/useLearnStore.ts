import { create } from "zustand";

export interface ChatMessage {
  id: string;
  role: "user" | "tutor";
  content: string;
  timestamp: Date;
}

interface LearnState {
  chatHistory: ChatMessage[];
  isTutorTyping: boolean;
  addMessage: (message: Omit<ChatMessage, "id" | "timestamp">) => void;
  setTyping: (status: boolean) => void;
  clearChat: () => void;
}

export const useLearnStore = create<LearnState>((set) => ({
  chatHistory: [],
  isTutorTyping: false,

  addMessage: (message) =>
    set((state) => {
      console.log(`[LearnStore] Adding new message from role: ${message.role}`);
      const newMessage: ChatMessage = {
        ...message,
        id: Math.random().toString(36).substring(2, 9),
        timestamp: new Date(),
      };
      return { chatHistory: [...state.chatHistory, newMessage] };
    }),

  setTyping: (status) =>
    set(() => {
      console.log(`[LearnStore] AI Tutor typing status: ${status}`);
      return { isTutorTyping: status };
    }),

  clearChat: () =>
    set(() => {
      console.log(`[LearnStore] Clearing chat history`);
      return { chatHistory: [] };
    }),
}));
