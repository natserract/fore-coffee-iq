import { createContext, useState } from "react";
import {
  ChatContextProps,
  ChatMessage,
} from "~/lib/context/ChatProvider/types";
import { useChatContext } from "~/lib/context/ChatProvider/hooks/useChatContext";

export const ChatContext = createContext<ChatContextProps | undefined>(
  undefined,
);

export function ChatProvider({
  children,
}: {
  children: JSX.Element | JSX.Element[];
}): JSX.Element {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const initChats = (chat: ChatMessage): void => {
    setMessages(() => [chat]);
  };

  const updateStreamingHistory = (streamedChat: ChatMessage): void => {
    setMessages((prevHistory: ChatMessage[]) => {
      const updatedHistory = prevHistory.find(
        (item) => item.message_id === streamedChat.message_id,
      )
        ? prevHistory.map((item: ChatMessage) =>
            item.message_id === streamedChat.message_id
              ? {
                  ...item,
                  assistant: item.assistant + streamedChat.assistant,
                  metadata: streamedChat.metadata,
                }
              : item,
          )
        : [...prevHistory, streamedChat];

      return updatedHistory;
    });
  };

  const removeMessage = (id: string): void => {
    setMessages((prevHistory: ChatMessage[]) =>
      prevHistory.filter((item) => item.message_id !== id),
    );
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        initChats,
        setMessages,
        removeMessage,
        updateStreamingHistory,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export const withChatContext = <P extends object>(
  Component: React.ComponentType<P>,
) => {
  return (props: P) => {
    return (
      <ChatProvider>
        <Component {...props} />
      </ChatProvider>
    );
  };
};
