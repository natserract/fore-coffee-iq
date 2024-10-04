import { ChatMessage } from "~/lib/context/ChatProvider/types";

type GeneratePlaceHolderMessageProps = {
  user_message: string;
  assistant: string;
  chat_id: string;
  type?: string;
};

export const generatePlaceHolderMessage = ({
  user_message,
  chat_id,
  assistant,
  type,
}: GeneratePlaceHolderMessageProps): ChatMessage => {
  return {
    message_id: new Date().getTime().toString(),
    message_time: new Date(
      new Date().setDate(new Date().getDate() + 1),
    ).toISOString(),
    chat_id,
    assistant,
    user_message,
    type,
  };
};
