"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="prose prose-invert max-w-none prose-table:border-collapse prose-th:border prose-th:border-slate-700 prose-td:border prose-td:border-slate-800">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          img: ({ ...props }) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              {...props}
              className="my-4 rounded-2xl border border-slate-800 shadow-lg"
              alt={props.alt ?? "Generated asset"}
            />
          )
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
