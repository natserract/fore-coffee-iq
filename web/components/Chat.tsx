"use client";
import { useState } from "react";
import { useHandleStream } from "~/hooks/useHandleStream";
import { withChatContext } from "~/lib/context/ChatProvider/ChatProvider";
import { useChatContext } from "~/lib/context/ChatProvider/hooks/useChatContext";
import { generatePlaceHolderMessage } from "~/utils/generatePlaceHolderMessage";

const Chat = () => {
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);

  const { handleStream } = useHandleStream();
  const { messages, removeMessage, updateStreamingHistory } = useChatContext();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPrompt(e.target.value);
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

    const query = prompt.trim();
    if (query.length === 0) {
      alert("prompt cannot be empty");
      return;
    }

    const headers = {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    };

    const placeHolderMessage = generatePlaceHolderMessage({
      user_message: query,
      chat_id: "1",
    });
    updateStreamingHistory(placeHolderMessage);

    const body = JSON.stringify({
      question: query,
    });

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
        "px-4 md:px-0 max-w-3xl mx-auto mt-20 flex flex-col justify-center items-center"
      }
    >
      <form
        onSubmit={handleSubmit}
        className={"w-[80%] space-y-2 flex flex-col mr-auto"}
      >
        <label htmlFor={"prompt"}>Enter a prompt</label>
        <input
          id={"prompt"}
          name={"prompt"}
          type={"text"}
          onChange={handleChange}
          className={"border border-purple-500 py-2 px-4 rounded-md"}
          placeholder={"Type here..."}
        />
        <div className={"text-right"}>
          <button
            disabled={generating}
            type={"submit"}
            className={
              "px-2 py-1 bg-blue-400 rounded-md text-white disabled:bg-blue-300 hover:bg-blue-500 disabled:cursor-not-allowed"
            }
          >
            Submit
          </button>
        </div>
      </form>
      <div
        className={
          "h-48 mt-4 w-full p-4 border border-purple-500 rounded-md overflow-auto"
        }
      >
        {messages.length > 0 ? (
          messages.map((content, idx) => {
            return (
              <div key={`assistant-${content.message_id}`}>
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
    </div>
  );
};

export default withChatContext(Chat);
