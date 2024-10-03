from langchain_core.messages.ai import AIMessageChunk
from typing import Any, Tuple, no_type_check
from models import RAGResponseMetadata

def cited_answer_filter(tool):
    return tool["name"] == "cited_answer"

@no_type_check
def parse_chunk_response(
    rolling_msg: AIMessageChunk,
    raw_chunk: dict[str, Any],
    supports_func_calling: bool,
) -> Tuple[AIMessageChunk, str]:
    answer_str = ""

    if "answer" in raw_chunk:
        answer = raw_chunk["answer"]
    else:
        answer = raw_chunk

    rolling_msg += AIMessageChunk(content=answer)
    if supports_func_calling and rolling_msg.tool_calls:
        cited_answer = next(x for x in rolling_msg.tool_calls if cited_answer_filter(x))
        if "args" in cited_answer and "answer" in cited_answer["args"]:
            gathered_args = cited_answer["args"]
            # Only send the difference between answer and response_tokens which was the previous answer
            answer_str = gathered_args["answer"]
            return rolling_msg, answer_str

    return rolling_msg, answer

def get_chunk_metadata(
    msg: AIMessageChunk, sources: list[Any] | None = None
) -> RAGResponseMetadata:
    # Initiate the source
    metadata = {"sources": sources} if sources else {"sources": []}
    if msg.tool_calls:
        cited_answer = next(x for x in msg.tool_calls if cited_answer_filter(x))

        if "args" in cited_answer:
            gathered_args = cited_answer["args"]
            if "citations" in gathered_args:
                citations = gathered_args["citations"]
                metadata["citations"] = citations

            if "followup_questions" in gathered_args:
                followup_questions = gathered_args["followup_questions"]
                metadata["followup_questions"] = followup_questions

    return RAGResponseMetadata(**metadata, metadata_model=None)
