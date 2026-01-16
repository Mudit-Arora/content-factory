export type ResearchResult = {
  contentIdea: string;
  strategy: string;
  imagePrompt: string;
};

export type GeneratedImage = {
  url: string;
  alt: string;
};

const MCP_BASE_URL =
  process.env.NEXT_PUBLIC_MCP_BASE_URL ?? "http://localhost:8000";

const request = async <T>(path: string, payload: unknown): Promise<T> => {
  let response: Response;
  try {
    response = await fetch(`${MCP_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (error) {
    const detail =
      error instanceof Error ? error.message : "Unknown network error";
    throw new Error(
      `MCP connection failed. Check NEXT_PUBLIC_MCP_BASE_URL. ${detail}`
    );
  }

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `MCP request failed (${response.status})`);
  }

  return (await response.json()) as T;
};

export async function getResearch(prompt: string): Promise<ResearchResult[]> {
  return request<ResearchResult[]>("/tools/get_research", { prompt });
}

export async function generateImages(
  prompts: string[]
): Promise<GeneratedImage[]> {
  return request<GeneratedImage[]>("/tools/generate_images", { prompts });
}
