export type ResearchResult = {
  contentIdea: string;
  strategy: string;
  imagePrompt: string;
};

export type GeneratedImage = {
  url: string;
  alt: string;
};

const request = async <T>(path: string, payload: unknown): Promise<T> => {
  let response: Response;
  try {
    response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (error) {
    const detail =
      error instanceof Error ? error.message : "Unknown network error";
    throw new Error(
      `MCP connection failed. Check server proxy. ${detail}`
    );
  }

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `MCP request failed (${response.status})`);
  }

  return (await response.json()) as T;
};

export async function getResearch(prompt: string): Promise<ResearchResult[]> {
  return request<ResearchResult[]>("/api/mcp/get_research", { prompt });
}

export async function generateImages(
  prompts: string[]
): Promise<GeneratedImage[]> {
  return request<GeneratedImage[]>("/api/mcp/generate_images", { prompts });
}
