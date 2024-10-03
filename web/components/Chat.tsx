"use client";

import ChatArea from "~/components/ChatArea";
import { ChatProvider } from "~/lib/context/ChatProvider/ChatProvider";

const Chat = () => {
  return (
    <ChatProvider>
      <ChatArea />
    </ChatProvider>
  );
};

export default Chat;
