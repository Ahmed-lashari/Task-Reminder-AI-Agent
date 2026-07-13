export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: number;
}

export interface Identity {
  name: string;
  ownerId: string;
}

export interface TechStackSection {
  label: string;
  items: string[];
}
