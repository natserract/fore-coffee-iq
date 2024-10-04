export type ChatConfig = {
  model: string;
  temperature: number;
  maxTokens: number;
};

export type MessageFrom = "human" | "ai";

export type ChatMessage = {
  chat_id: string;
  message_id: string;
  user_message: string;
  assistant: string;
  message_time: string;
  metadata?: Record<string, any>;
  message_type: MessageFrom;
};

export type ChatContextProps = {
  messages: ChatMessage[];
  setMessages: (history: ChatMessage[]) => void;
  updateStreamingHistory: (streamedChat: ChatMessage) => void;
  initChats: (chat: ChatMessage) => void;
  removeMessage: (id: string) => void;
};
