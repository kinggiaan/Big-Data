/**
 * Cloudflare Worker — Academic Paper Search API
 *
 * Routes:
 *   GET /api/search?q=...&mode=hybrid|bm25|knn&size=10&yearMin=&yearMax=&categories=cs.LG,cs.AI
 *   GET /api/categories
 *   GET /api/years
 *   GET /api/stats
 *   GET /*  → serve static frontend (via Pages, or fallback 404)
 */
import { Hono } from "hono";
import { cors } from "hono/cors";
import type { Env, SearchMode, SearchResponse } from "./types";
import { bm25Search, knnSearch, hybridSearch } from "./search";

const app = new Hono<{ Bindings: Env }>();

// Enable CORS for frontend
app.use("/api/*", cors());

// ─── Search endpoint ────────────────────────────────────────────────────────
app.get("/api/search", async (c) => {
  const query = c.req.query("q")?.trim();
  if (!query) {
    return c.json({ error: "Missing query parameter 'q'" }, 400);
  }

  const mode = (c.req.query("mode") || "hybrid") as SearchMode;
  const size = Math.min(parseInt(c.req.query("size") || "10"), 20);
  const yearMin = c.req.query("yearMin") || undefined;
  const yearMax = c.req.query("yearMax") || undefined;
  const categoriesParam = c.req.query("categories");
  const categories = categoriesParam
    ? categoriesParam.split(",").filter(Boolean)
    : undefined;

  const start = Date.now();

  try {
    let hits;
    switch (mode) {
      case "bm25":
        hits = await bm25Search(
          c.env,
          query,
          size,
          yearMin,
          yearMax,
          categories
        );
        break;
      case "knn":
        hits = await knnSearch(
          c.env,
          query,
          size,
          yearMin,
          yearMax,
          categories
        );
        break;
      case "hybrid":
      default:
        hits = await hybridSearch(
          c.env,
          query,
          size,
          yearMin,
          yearMax,
          categories
        );
        break;
    }

    const latency = Date.now() - start;
    const response: SearchResponse = {
      hits,
      total: hits.length,
      latency_ms: latency,
      mode,
    };

    return c.json(response);
  } catch (err: any) {
    console.error("Search error:", err);
    return c.json({ error: err.message || "Search failed" }, 500);
  }
});

// ─── Categories endpoint ────────────────────────────────────────────────────
app.get("/api/categories", async (c) => {
  const result = await c.env.DB.prepare(
    `SELECT categories, COUNT(*) as cnt FROM papers
     GROUP BY categories ORDER BY cnt DESC LIMIT 100`
  ).all<{ categories: string; cnt: number }>();

  // Extract unique individual categories
  const catCounts = new Map<string, number>();
  for (const row of result.results || []) {
    const cats = row.categories.split(" ");
    for (const cat of cats) {
      if (cat) catCounts.set(cat, (catCounts.get(cat) || 0) + row.cnt);
    }
  }

  const sorted = [...catCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => ({ name, count }));

  return c.json({ categories: sorted });
});

// ─── Year range endpoint ────────────────────────────────────────────────────
app.get("/api/years", async (c) => {
  const result = await c.env.DB.prepare(
    `SELECT MIN(CAST(year AS INTEGER)) as min_year,
            MAX(CAST(year AS INTEGER)) as max_year
     FROM papers WHERE year != '' AND year IS NOT NULL`
  ).first<{ min_year: number; max_year: number }>();

  return c.json({
    min: result?.min_year || 2007,
    max: result?.max_year || 2026,
  });
});

// ─── Stats endpoint ─────────────────────────────────────────────────────────
app.get("/api/stats", async (c) => {
  const count = await c.env.DB.prepare(
    "SELECT COUNT(*) as total FROM papers"
  ).first<{ total: number }>();

  return c.json({
    documents: count?.total || 0,
    index: "arxiv-search (D1 + Vectorize)",
    search_modes: ["hybrid", "bm25", "knn"],
  });
});

// ─── Health check ───────────────────────────────────────────────────────────
app.get("/api/health", (c) => c.json({ status: "ok" }));

// ─── Fallback ───────────────────────────────────────────────────────────────
app.all("*", (c) => {
  return c.json({
    message: "Academic Paper Search API",
    endpoints: ["/api/search", "/api/categories", "/api/years", "/api/stats"],
  });
});

export default app;
