/**
 * Search logic — mirrors the Python implementation in src/ui/app.py
 *
 * BM25 (keyword)  →  D1 FTS5
 * kNN  (vector)   →  Vectorize
 * Hybrid (RRF)    →  Both combined via Reciprocal Rank Fusion
 */
import type { Env, PaperRecord, SearchHit } from "./types";

const RRF_K = 60;

// ─── BM25 (Keyword) Search via D1 FTS5 ─────────────────────────────────────
export async function bm25Search(
  env: Env,
  query: string,
  size: number,
  yearMin?: string,
  yearMax?: string,
  categories?: string[]
): Promise<SearchHit[]> {
  // FTS5 query: wrap each word for prefix matching
  const ftsQuery = query
    .trim()
    .split(/\s+/)
    .map((w) => `"${w}"`)
    .join(" ");

  // Build WHERE clauses for filters
  const filterClauses: string[] = [];
  const params: (string | number)[] = [];

  if (yearMin && yearMax) {
    filterClauses.push("p.year >= ? AND p.year <= ?");
    params.push(yearMin, yearMax);
  }
  if (categories && categories.length > 0) {
    // Match any of the selected categories
    const catConditions = categories.map(() => "p.categories LIKE ?");
    filterClauses.push(`(${catConditions.join(" OR ")})`);
    categories.forEach((c) => params.push(`%${c}%`));
  }

  const filterSQL =
    filterClauses.length > 0 ? "AND " + filterClauses.join(" AND ") : "";

  const sql = `
    SELECT p.id, p.title, p.abstract, p.authors, p.year, p.categories,
           fts.rank AS score
    FROM papers_fts fts
    JOIN papers p ON p.rowid = fts.rowid
    WHERE papers_fts MATCH ?
    ${filterSQL}
    ORDER BY fts.rank
    LIMIT ?
  `;

  const result = await env.DB.prepare(sql)
    .bind(ftsQuery, ...params, size)
    .all<PaperRecord & { score: number }>();

  return (result.results || []).map((row, i) => ({
    id: row.id,
    title: row.title,
    abstract: row.abstract,
    authors: row.authors,
    year: row.year,
    categories: row.categories ? row.categories.split(" ") : [],
    score: Math.abs(row.score || 0), // FTS5 rank is negative
    highlights: highlightText(query, row.title, row.abstract),
  }));
}

// ─── kNN (Vector) Search via Vectorize ──────────────────────────────────────
export async function knnSearch(
  env: Env,
  query: string,
  size: number,
  yearMin?: string,
  yearMax?: string,
  categories?: string[]
): Promise<SearchHit[]> {
  // Generate query embedding using Workers AI
  const embeddingResponse = await env.AI.run(
    "@cf/baai/bge-small-en-v1.5" as any,
    { text: [query] }
  );
  const queryVector = (embeddingResponse as any).data[0];

  // Query Vectorize for nearest neighbors
  // returnMetadata:"all" limits topK to 50; "indexed" allows up to 100
  const topK = Math.min(size * 2, 50);
  const vectorResults = await env.VECTORIZE.query(queryVector, {
    topK,
    returnMetadata: "indexed",
  });

  if (!vectorResults.matches || vectorResults.matches.length === 0) {
    return [];
  }

  // Get paper IDs from vector results
  const ids = vectorResults.matches.map((m) => m.id);

  // Fetch full paper data from D1
  const placeholders = ids.map(() => "?").join(",");
  let filterSQL = "";
  const filterParams: string[] = [];

  if (yearMin && yearMax) {
    filterSQL += " AND year >= ? AND year <= ?";
    filterParams.push(yearMin, yearMax);
  }
  if (categories && categories.length > 0) {
    const catConditions = categories.map(() => "categories LIKE ?");
    filterSQL += ` AND (${catConditions.join(" OR ")})`;
    categories.forEach((c) => filterParams.push(`%${c}%`));
  }

  const sql = `SELECT id, title, abstract, authors, year, categories
               FROM papers WHERE id IN (${placeholders}) ${filterSQL}`;

  const result = await env.DB.prepare(sql)
    .bind(...ids, ...filterParams)
    .all<PaperRecord>();

  // Build lookup map
  const paperMap = new Map<string, PaperRecord>();
  (result.results || []).forEach((p) => paperMap.set(p.id, p));

  // Merge vector scores with paper data
  const hits: SearchHit[] = [];
  for (const match of vectorResults.matches) {
    const paper = paperMap.get(match.id);
    if (!paper) continue; // Filtered out
    hits.push({
      id: paper.id,
      title: paper.title,
      abstract: paper.abstract,
      authors: paper.authors,
      year: paper.year,
      categories: paper.categories ? paper.categories.split(" ") : [],
      score: match.score || 0,
    });
    if (hits.length >= size) break;
  }

  return hits;
}

// ─── Hybrid Search (RRF) ───────────────────────────────────────────────────
export async function hybridSearch(
  env: Env,
  query: string,
  size: number,
  yearMin?: string,
  yearMax?: string,
  categories?: string[]
): Promise<SearchHit[]> {
  const fetchSize = Math.max(size * 3, 30);

  // Run BM25 and kNN in parallel
  const [bm25Hits, knnHits] = await Promise.all([
    bm25Search(env, query, fetchSize, yearMin, yearMax, categories),
    knnSearch(env, query, fetchSize, yearMin, yearMax, categories),
  ]);

  // RRF merge — same formula as Python: score(d) = Σ 1/(k + rank)
  const scores = new Map<string, number>();
  const docs = new Map<string, SearchHit>();

  bm25Hits.forEach((hit, i) => {
    const rank = i + 1;
    scores.set(hit.id, (scores.get(hit.id) || 0) + 1.0 / (RRF_K + rank));
    docs.set(hit.id, hit);
  });

  knnHits.forEach((hit, i) => {
    const rank = i + 1;
    scores.set(hit.id, (scores.get(hit.id) || 0) + 1.0 / (RRF_K + rank));
    if (!docs.has(hit.id)) {
      docs.set(hit.id, hit);
    }
  });

  // Sort by RRF score descending
  const ranked = [...scores.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, size);

  return ranked.map(([id, rrfScore]) => ({
    ...docs.get(id)!,
    score: rrfScore,
  }));
}

// ─── Highlight helper ───────────────────────────────────────────────────────
function highlightText(
  query: string,
  title: string,
  abstract: string
): { title?: string; abstract?: string } {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  const highlights: { title?: string; abstract?: string } = {};

  let hlTitle = title;
  let hlAbstract = abstract.slice(0, 300);

  for (const word of words) {
    const regex = new RegExp(`(${escapeRegex(word)})`, "gi");
    hlTitle = hlTitle.replace(regex, "<mark>$1</mark>");
    hlAbstract = hlAbstract.replace(regex, "<mark>$1</mark>");
  }

  if (hlTitle !== title) highlights.title = hlTitle;
  if (hlAbstract !== abstract.slice(0, 300)) highlights.abstract = hlAbstract;

  return highlights;
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
