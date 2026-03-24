import { Bot, User } from "lucide-react";

export interface Message {
  id: string;
  role: "bot" | "user";
  content: string;
  timestamp: string;
}
export const ChatMessage = ({ message }: { message: Message }) => {
  const isBot = message.role === "bot";

  return (
    <div className={`flex items-start gap-3 ${isBot ? "" : "flex-row-reverse"}`}>
      <div
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
          isBot ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
        }`}
      >
        {isBot ? <Bot className="h-5 w-5" /> : <User className="h-5 w-5" />}
      </div>
      <div className="flex flex-col gap-1">
        <div className={isBot ? "chat-bubble-bot" : "chat-bubble-user"}>
          {message.content}
        </div>
        <span className={`text-xs text-muted-foreground ${isBot ? "" : "text-right"}`}>
          {message.timestamp}
        </span>
      </div>
    </div>
  );
};

export default ChatMessage;
