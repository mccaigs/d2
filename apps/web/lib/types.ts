export type MessageRole = "user" | "assistant";

export interface SourceChip {
  label: string;
  category: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  sources?: SourceChip[];
  followUps?: string[];
  isStreaming?: boolean;
  showContactForm?: boolean;
  contactReason?: string | null;
}

export interface StreamChunk {
  type: "chunk";
  content: string;
}

export interface StreamMetadata {
  type: "metadata";
  sources: SourceChip[];
  follow_ups: string[];
  intent: string;
  show_contact_form?: boolean;
  contact_reason?: string | null;
}

export type StreamEvent = StreamChunk | StreamMetadata;

export interface FitGap {
  area: string;
  note: string;
}

export interface ProjectMatch {
  name: string;
  reason: string;
}

export interface ScoreBreakdown {
  technical: number;
  applied_ai: number;
  product_architecture: number;
  domain: number;
  seniority: number;
}

export interface FitResponse {
  summary: string;
  overall_score: number;
  fit_label: string;
  breakdown: ScoreBreakdown;
  confidence: "high" | "medium" | "low";
  confidence_reason: string;
  strengths: string[];
  gaps: FitGap[];
  relevant_projects: ProjectMatch[];
  talking_points: string[];
}
