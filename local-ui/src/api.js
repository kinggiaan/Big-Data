const API_BASE = "http://localhost:8000/api";

export async function searchPapers(query, mode = "hybrid", size = 10, filters = {}) {
  const url = new URL(`${API_BASE}/search`);
  url.searchParams.append("q", query);
  url.searchParams.append("mode", mode);
  url.searchParams.append("size", size);
  
  if (filters.yearMin) url.searchParams.append("yearMin", filters.yearMin);
  if (filters.yearMax) url.searchParams.append("yearMax", filters.yearMax);
  if (filters.categories && filters.categories.length > 0) {
    url.searchParams.append("categories", filters.categories.join(","));
  }

  const response = await fetch(url.toString());
  if (!response.ok) throw new Error("Search failed");
  return response.json();
}

export async function getCategories() {
  const response = await fetch(`${API_BASE}/categories`);
  if (!response.ok) throw new Error("Failed to fetch categories");
  return response.json();
}

export async function getYears() {
  const response = await fetch(`${API_BASE}/years`);
  if (!response.ok) throw new Error("Failed to fetch years");
  return response.json();
}

export async function getStats() {
  const response = await fetch(`${API_BASE}/stats`);
  if (!response.ok) throw new Error("Failed to fetch stats");
  return response.json();
}

export async function ingestPapers(papers) {
  const response = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(papers)
  });
  if (!response.ok) throw new Error("Failed to ingest papers");
  return response.json();
}
