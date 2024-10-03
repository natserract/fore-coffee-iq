export type ChatConfig = {
  model: string;
  temperature: number;
  maxTokens: number;
};

export type ChatMessage = {
  chat_id: string;
  message_id: string;
  user_message: string;
  assistant: string;
  message_time: string;
  metadata?: Record<string, any>;
};

export type ChatContextProps = {
  messages: ChatMessage[];
  setMessages: (history: ChatMessage[]) => void;
  updateStreamingHistory: (streamedChat: ChatMessage) => void;
  removeMessage: (id: string) => void;
};
