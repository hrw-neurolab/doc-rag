export interface User {
  _id: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface CreateUserBody {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
}

export type TokensWithUser = Tokens & {
  user: User;
};

interface BaseResource {
  _id: string;
  type: "pdf" | "webpage";
  title: string;
  user: string;
  created_at: string;
}

export interface PdfResource extends BaseResource {
  total_pages: number;
}

export interface WebpageResource extends BaseResource {
  url: string;
}

export type Resource = PdfResource | WebpageResource;

export interface ResourceChatBody {
  query: string;
  resource_ids?: string[];
}

export interface BaseChunk {
  _id: string;
  user: string;
  resource: string;
  content: string;
}

export interface PdfChunk extends BaseChunk {
  page_number: number;
}

export type WebpageChunk = BaseChunk;

export type Chunk = PdfChunk | WebpageChunk;
