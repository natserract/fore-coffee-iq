"use client";
import Image from "next/image";
import { useEffect, useState } from "react";
import { useHandleStream } from "~/hooks/useHandleStream";
import { withChatContext } from "~/lib/context/ChatProvider/ChatProvider";
import { useChatContext } from "~/lib/context/ChatProvider/hooks/useChatContext";
import { generatePlaceHolderMessage } from "~/utils/generatePlaceHolderMessage";

const Chat = () => {
  const [query, setQuery] = useState("");
  const [generating, setGenerating] = useState(false);
  const [processTime, setProcessTime] = useState<string | null>(null);

  const { handleStream } = useHandleStream();
  const { messages, initChats, removeMessage, updateStreamingHistory } =
    useChatContext();

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

    const questionMessage = generatePlaceHolderMessage({
      user_message: question,
      assistant: question,
      chat_id: new Date().getTime().toString(),
      message_type: "human",
    });
    updateStreamingHistory(questionMessage);

    const body = JSON.stringify({
      question: question,
    });

    setQuery("");
    setGenerating(true);
    setProcessTime(null);
    try {
      const startTime = performance.now();
      const response = await fetch("/api/chat", {
        headers,
        method: "POST",
        body,
      });
      console.debug("response", response);

      if (!response.ok) {
        void handleFetchError(response);
        return;
      }

      if (response.body === null) {
        throw new Error("Response Body Null");
      }

      await handleStream(response.body.getReader());

      // Show total time
      const endTime = performance.now();
      const processTimeInSeconds = (endTime - startTime) / 1000;
      setProcessTime(processTimeInSeconds.toFixed(2));
    } catch (error) {
      //@ts-ignore
      alert(`error: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  // Greetings
  useEffect(() => {
    // In development mode, will show two times
    updateStreamingHistory({
      message_id: new Date().getTime().toString(),
      message_time: new Date(
        new Date().setDate(new Date().getDate() + 1),
      ).toISOString(),
      user_message: "welcome",
      assistant: "Hi Fore Friends! Selamat datang di Fore Coffee! 😘",
      chat_id: new Date().getTime().toString(),
      message_type: "ai",
    });
  }, []);

  return (
    <div
      className={
        "px-4 md:px-0 max-w-3xl mx-auto flex flex-col justify-center items-center"
      }
    >
      <div
        className={
          "pt-10 relative w-full h-[86vh] overflow-auto transition-width"
        }
      >
        {messages.length > 0 ? (
          messages.map((content, idx) => {
            const isHuman = content.message_type == "human";

            return (
              <div
                className={`mb-3 flex items-start ${isHuman ? "justify-end text-right" : "justify-start text-left"} gap-x-5`}
                key={`assistant-${content.message_id}`}
              >
                {!isHuman ? (
                  <div className="w-[40px]">
                    <Image
                      src="/logo-single.png"
                      width={40}
                      height={40}
                      alt="Fore Coffee"
                    />
                  </div>
                ) : null}{" "}
                <p className="w-[95%] pt-2">{content.assistant}</p>
              </div>
            );
          })
        ) : (
          <h2 className={"h-full flex justify-center items-center"}>
            No Response
          </h2>
        )}

        {generating && (
          <div className={`mb-3 flex items-start justify-start gap-x-5`}>
            <div className="w-[40px]">
              <Image
                src="/logo-single.png"
                width={40}
                height={40}
                alt="Fore Coffee"
              />
            </div>
            <span className="w-[95%] pt-2">...</span>
          </div>
        )}
      </div>

      <div className="md:pt-0 dark:border-white/20 md:border-transparent md:dark:border-transparent w-full">
        <form onSubmit={handleSubmit} className={"mt-5 space-y-2 w-full"}>
          {processTime && !generating && (
            <time className="text-xs text-gray-400">
              Total time: {processTime}s
            </time>
          )}

          <div className="relative">
            <input
              id={"query"}
              name={"query"}
              type={"text"}
              onChange={handleChange}
              value={query}
              className="border border-gray-300 rounded-lg pl-4 pr-20 py-2 w-full focus:outline-none placeholder:text-gray-500"
              placeholder={"Ada yang bisa kami bantu?"}
              autoComplete="off"
            />
            <button
              disabled={generating || !query.length}
              type={"submit"}
              className="absolute right-0 top-0 bottom-0 bg-black hover:bg-zinc-900 text-white rounded-md px-4 py-2 disabled:cursor-not-allowed disabled:bg-zinc-300"
            >
              Chat
            </button>
          </div>
        </form>
        <p className="mt-4 text-sm text-gray-500 text-center">
          ForeCoffeeIQ can make mistakes. Check important info.
        </p>
      </div>
    </div>
  );
};

export default withChatContext(Chat);
