/** Type definitions for the Cloudflare Worker API */

export interface Env {
  DB: D1Database;
  VECTORIZE: VectorizeIndex;
  AI: Ai;
}

export interface PaperRecord {
  id: string;
  title: string;
  abstract: string;
  authors: string;
  year: string;
  categories: string;
}

export interface SearchHit {
  id: string;
  title: string;
  abstract: string;
  authors: string;
  year: string;
  categories: string[];
  score: number;
  highlights?: {
    title?: string;
    abstract?: string;
  };
}

export interface SearchResponse {
  hits: SearchHit[];
  total: number;
  latency_ms: number;
  mode: string;
}

export type SearchMode = "hybrid" | "bm25" | "knn";
