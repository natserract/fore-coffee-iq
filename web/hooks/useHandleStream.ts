import { useChatContext } from "~/lib/context/ChatProvider/hooks/useChatContext";

export const useHandleStream = () => {
  const { updateStreamingHistory } = useChatContext();

  const handleStream = async (
    reader: ReadableStreamDefaultReader<Uint8Array>,
    onFirstChunk?: () => void,
  ): Promise<void> => {
    const decoder = new TextDecoder("utf-8");
    let isFirstChunk = true;
    let incompleteData = "";

    const handleStreamRecursively = async () => {
      const { done, value } = await reader.read();
      if (done) {
        if (incompleteData !== "") {
          try {
            const parsedData = JSON.parse(incompleteData);
            updateStreamingHistory(parsedData);
          } catch (e) {
            console.error("Error parsing incomplete data", e);
          }
        }

        return;
      }

      if (isFirstChunk) {
        isFirstChunk = false;
        if (onFirstChunk) {
          onFirstChunk();
        }
      }

      // Concatenate incomplete data with new chunk
      const rawData = incompleteData + decoder.decode(value, { stream: true });
      const dataStrings = rawData.trim().split("data: ").filter(Boolean);

      dataStrings.forEach((data, index, array) => {
        if (index === array.length - 1 && !data.endsWith("\n")) {
          // Last item and does not end with a newline, save as incomplete
          incompleteData = data;

          return;
        }

        try {
          const parsedData = JSON.parse(data);
          updateStreamingHistory(parsedData);
        } catch (e) {
          console.error("Error parsing data string", e);
        }
      });

      await handleStreamRecursively();
    };

    await handleStreamRecursively();
  };

  return {
    handleStream,
  };
};
