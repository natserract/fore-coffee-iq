"use client";
import { useState } from "react";
import { useHandleStream } from "~/hooks/useHandleStream";
import { withChatContext } from "~/lib/context/ChatProvider/ChatProvider";
import { useChatContext } from "~/lib/context/ChatProvider/hooks/useChatContext";
import { generatePlaceHolderMessage } from "~/utils/generatePlaceHolderMessage";

const Chat = () => {
  const [query, setQuery] = useState("");
  const [chatHistories, setChatHistories] = useState<
    { human: string; ai: string }[]
  >([]);
  const [generating, setGenerating] = useState(false);

  const { handleStream } = useHandleStream();
  const { messages, removeMessage, updateStreamingHistory } = useChatContext();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleFetchError = async (response: Response) => {
    if (response.status === 429) {
      console.error("Too ManyRequests");
      return;
    }

    const errorMessage = await response.json();
    console.error(errorMessage);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const question = query.trim();
    if (question.length === 0) {
      alert("Question cannot be empty");
      return;
    }

    const headers = {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    };

    const placeHolderMessage = generatePlaceHolderMessage({
      user_message: question,
      chat_id: "1",
    });
    updateStreamingHistory(placeHolderMessage);

    const body = JSON.stringify({
      question: question,
    });

    setQuery("");
    setGenerating(true);
    try {
      const response = await fetch("/api/chat", {
        headers,
        method: "POST",
        body,
      });
      if (!response.ok) {
        void handleFetchError(response);
        return;
      }

      if (response.body === null) {
        throw new Error("Response Body Null");
      }

      await handleStream(response.body.getReader(), () =>
        removeMessage(placeHolderMessage.message_id),
      );
    } catch (error) {
      //@ts-ignore
      alert(`error: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div
      className={
        "px-4 md:px-0 max-w-3xl mx-auto flex flex-col justify-center items-center"
      }
    >
      <div
        className={
          "h-[80vh] mt-4 w-full p-4 border border-slate-300 rounded-md overflow-auto"
        }
      >
        {messages.length > 0 ? (
          messages.map((content, idx) => {
            return (
              <div
                className="mb-5 bg-slate-200 p-5"
                key={`assistant-${content.message_id}`}
              >
                {content.assistant}
              </div>
            );
          })
        ) : (
          <h2 className={"h-full flex justify-center items-center"}>
            No Response
          </h2>
        )}
      </div>

      <form onSubmit={handleSubmit} className={"mt-5 space-y-2 w-full"}>
        <div className="relative">
          <input
            id={"query"}
            name={"query"}
            type={"text"}
            onChange={handleChange}
            value={query}
            className="border border-gray-300 rounded-lg pl-4 pr-20 py-2 w-full focus:outline-none"
            placeholder={"Enter a question"}
          />
          <button
            disabled={generating}
            type={"submit"}
            className="absolute right-0 top-0 bottom-0 bg-black hover:bg-zinc-900 text-white rounded-md px-4 py-2 disabled:cursor-not-allowed disabled:bg-zinc-900"
          >
            Submit
          </button>
        </div>
      </form>
    </div>
  );
};

export default withChatContext(Chat);
