"use client";

import QA from "~/components/QA";
import { ChatProvider } from "~/lib/context/ChatProvider/ChatProvider";

const Chat = () => {
  return (
    <ChatProvider>
      <QA />
    </ChatProvider>
  );
};

export default Chat;
