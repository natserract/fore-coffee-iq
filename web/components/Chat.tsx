"use client";
import { useState } from "react";
import { useHandleStream } from "~/hooks/useHandleStream";
import { withChatContext } from "~/lib/context/ChatProvider/ChatProvider";
import { useChatContext } from "~/lib/context/ChatProvider/hooks/useChatContext";
import { generatePlaceHolderMessage } from "~/utils/generatePlaceHolderMessage";

const Chat = () => {
  const [query, setQuery] = useState("");
  const [chatHistories, setChatHistories] = useState<
    { human: string; ai: string | null }[]
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

    let messageIdx = chatHistories.length;
    setChatHistories((state) => {
      return [
        ...state,
        {
          human: question,
          ai: null,
        },
      ];
    });

    const headers = {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    };

    const questionMessage = generatePlaceHolderMessage({
      user_message: question,
      assistant: question,
      chat_id: new Date().getTime().toString(),
    });
    updateStreamingHistory(questionMessage);

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

      await handleStream(response.body.getReader());
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
          "pt-5 relative w-full h-[90vh] overflow-auto transition-width"
        }
      >
        {messages.length > 0 ? (
          messages.map((content, idx) => {
            const isEven = idx % 2 == 0;

            return (
              <div
                className={`mb-3 p-3 flex items-center ${isEven ? "justify-end" : "justify-start"}`}
                key={`assistant-${content.message_id}`}
              >
                {!isEven ? <span className="p-5">🧠</span> : null}{" "}
                <p>{content.assistant}</p>
              </div>
            );
          })
        ) : (
          <h2 className={"h-full flex justify-center items-center"}>
            No Response
          </h2>
        )}

        {generating && (
          <div className="mb-3 p-3">
            <span className="p-5 text-gray-400">🧠</span> ...
          </div>
        )}
      </div>

      <div className="md:pt-0 dark:border-white/20 md:border-transparent md:dark:border-transparent w-full">
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
              disabled={generating || !query.length}
              type={"submit"}
              className="absolute right-0 top-0 bottom-0 bg-black hover:bg-zinc-900 text-white rounded-md px-4 py-2 disabled:cursor-not-allowed disabled:bg-zinc-300"
            >
              Ask
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default withChatContext(Chat);
