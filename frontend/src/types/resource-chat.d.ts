export interface UserMessage {
  role: "user";
  content: string;
}

interface AssistantMessageContent {
  text: string;
  citations: string[];
}

export interface AssistantMessage {
  role: "assistant";
  content: AssistantMessageContent;
}

export type Message = UserMessage | AssistantMessage;
