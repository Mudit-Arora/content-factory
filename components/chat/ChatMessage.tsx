"use client";

import { motion } from "framer-motion";
import MarkdownRenderer from "./MarkdownRenderer";

export type ChatMessageType = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export default function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-lg ${
          isUser
            ? "bg-indigo-500 text-white"
            : "bg-slate-900/70 text-slate-100"
        }`}
      >
        {isUser ? (
          <div>{message.content}</div>
        ) : (
          <MarkdownRenderer content={message.content} />
        )}
      </div>
    </motion.div>
  );
}
