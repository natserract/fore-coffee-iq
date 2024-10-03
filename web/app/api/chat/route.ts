import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.json();
  const { question } = body;

  const response = await fetch("http://0.0.0.0:8000/chat", {
    method: "POST",
    headers: {
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json",
      "Cache-Control": "no-cache",
    },
    body: JSON.stringify({
      question: question,
    }),
  });
  if (!response.ok) {
    return NextResponse.json(
      { error: "Failed to fetch from external API" },
      { status: 500 },
    );
  }

  const reader = response.body?.getReader();
  if (!reader) {
    return NextResponse.json({ error: "No data available" }, { status: 500 });
  }

  const stream = new ReadableStream({
    async start(controller) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          controller.close();
          break;
        }
        // Decode the incoming chunk and send it as an event
        const text = new TextDecoder().decode(value);
        controller.enqueue(text);
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
