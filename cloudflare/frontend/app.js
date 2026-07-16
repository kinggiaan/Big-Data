/**
 * Academic Paper Search — Client-side JavaScript
 * Connects to the Cloudflare Worker API
 */

const API_BASE = "https://arxiv-search-api.dgan-sdh241.workers.dev";

// ─── State ──────────────────────────────────────────────────────────────────
let currentMode = "hybrid";
let selectedCategories = [];

// ─── DOM Elements ───────────────────────────────────────────────────────────
const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");
const resultsContainer = document.getElementById("results");
const statsBar = document.getElementById("stats-bar");
const emptyState = document.getElementById("empty-state");
const chartContainer = document.getElementById("chart-container");
const filterToggle = document.getElementById("filter-toggle");
const filtersPanel = document.getElementById("filters-panel");
const yearFilterCheck = document.getElementById("year-filter-check");
const yearRangeContainer = document.getElementById("year-range-container");
const yearMinInput = document.getElementById("year-min");
const yearMaxInput = document.getElementById("year-max");
const categoryChips = document.getElementById("category-chips");
const resultSizeSelect = document.getElementById("result-size");

// ─── Init ───────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadStats();
  loadCategories();
  loadYears();

  // Search on Enter
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") doSearch();
  });

  // Search button
  searchBtn.addEventListener("click", doSearch);

  // Mode buttons
  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".mode-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentMode = btn.dataset.mode;
    });
  });

  // Filter toggle
  filterToggle.addEventListener("click", () => {
    const visible = filtersPanel.style.display !== "none";
    filtersPanel.style.display = visible ? "none" : "block";
    filterToggle.classList.toggle("active", !visible);
  });

  // Year filter checkbox
  yearFilterCheck.addEventListener("change", () => {
    yearRangeContainer.style.display = yearFilterCheck.checked ? "flex" : "none";
  });

  // Example queries
  document.querySelectorAll(".example-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      searchInput.value = btn.dataset.query;
      doSearch();
    });
  });
});

// ─── Search ─────────────────────────────────────────────────────────────────
async function doSearch() {
  const query = searchInput.value.trim();
  if (!query) return;

  const size = resultSizeSelect.value;

  // Build URL
  let url = `${API_BASE}/api/search?q=${encodeURIComponent(query)}&mode=${currentMode}&size=${size}`;

  if (yearFilterCheck.checked) {
    const yMin = yearMinInput.value;
    const yMax = yearMaxInput.value;
    if (yMin) url += `&yearMin=${yMin}`;
    if (yMax) url += `&yearMax=${yMax}`;
  }

  if (selectedCategories.length > 0) {
    url += `&categories=${selectedCategories.join(",")}`;
  }

  // Show loading
  emptyState.style.display = "none";
  statsBar.style.display = "none";
  chartContainer.style.display = "none";
  resultsContainer.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  try {
    const resp = await fetch(url);
    const data = await resp.json();

    if (data.error) {
      resultsContainer.innerHTML = `<div class="error-msg">⚠️ ${data.error}</div>`;
      return;
    }

    renderStats(data);
    renderResults(data.hits);
    renderChart(data.hits);
  } catch (err) {
    resultsContainer.innerHTML = `<div class="error-msg">⚠️ Network error: ${err.message}</div>`;
  }
}

// ─── Render Stats ───────────────────────────────────────────────────────────
function renderStats(data) {
  document.getElementById("stat-results").textContent = data.total;
  document.getElementById("stat-latency").textContent = `${data.latency_ms}ms`;

  const modeLabels = { hybrid: "Hybrid", bm25: "BM25", knn: "kNN" };
  document.getElementById("stat-mode").textContent = modeLabels[data.mode] || data.mode;

  statsBar.style.display = "flex";
}

// ─── Render Results ─────────────────────────────────────────────────────────
function renderResults(hits) {
  if (!hits || hits.length === 0) {
    resultsContainer.innerHTML = `
      <div class="no-results">
        <div class="no-results-icon">📭</div>
        <p>No results found. Try a different query or search mode.</p>
      </div>`;
    return;
  }

  resultsContainer.innerHTML = hits
    .map((hit, i) => {
      const title = hit.highlights?.title || escapeHtml(hit.title);
      const abstractText = hit.highlights?.abstract || escapeHtml((hit.abstract || "").slice(0, 300));
      const ellipsis = hit.abstract && hit.abstract.length > 300 && !hit.highlights?.abstract ? "..." : "";
      const categories = Array.isArray(hit.categories) ? hit.categories : (hit.categories || "").split(" ");
      const authors = (hit.authors || "Unknown").slice(0, 120);

      const delay = i * 50;

      return `
        <div class="result-card" style="animation-delay: ${delay}ms">
          <div class="result-header">
            <span class="result-rank">${i + 1}</span>
            <span class="result-title">${title}</span>
          </div>
          <div class="result-meta">
            <span class="meta-item"><span class="meta-icon">👤</span> ${escapeHtml(authors)}</span>
            <span class="meta-item"><span class="meta-icon">📅</span> ${hit.year || "N/A"}</span>
            <span class="meta-item"><span class="meta-icon">🆔</span> ${hit.id}</span>
          </div>
          <div class="result-abstract">${abstractText}${ellipsis}</div>
          <div class="result-tags">
            ${categories.filter(Boolean).map((c) => `<span class="result-tag">${escapeHtml(c)}</span>`).join("")}
            <span class="result-score">Score: ${hit.score.toFixed(6)}</span>
          </div>
        </div>`;
    })
    .join("");
}

// ─── Render Chart ───────────────────────────────────────────────────────────
function renderChart(hits) {
  if (!hits || hits.length === 0) {
    chartContainer.style.display = "none";
    return;
  }

  // Count categories
  const counts = {};
  hits.forEach((h) => {
    const cats = Array.isArray(h.categories) ? h.categories : (h.categories || "").split(" ");
    cats.forEach((c) => {
      if (c) counts[c] = (counts[c] || 0) + 1;
    });
  });

  const sorted = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  if (sorted.length === 0) {
    chartContainer.style.display = "none";
    return;
  }

  const maxCount = sorted[0][1];
  const chartDiv = document.getElementById("chart");

  chartDiv.innerHTML = sorted
    .map(
      ([cat, count]) => `
      <div class="chart-bar-row">
        <span class="chart-label">${escapeHtml(cat)}</span>
        <div class="chart-bar-track">
          <div class="chart-bar-fill" style="width: ${(count / maxCount) * 100}%"></div>
        </div>
        <span class="chart-count">${count}</span>
      </div>`
    )
    .join("");

  chartContainer.style.display = "block";
}

// ─── Load categories ────────────────────────────────────────────────────────
async function loadCategories() {
  try {
    const resp = await fetch(`${API_BASE}/api/categories`);
    const data = await resp.json();

    if (data.categories && data.categories.length > 0) {
      categoryChips.innerHTML = data.categories
        .map(
          (c) => `<span class="cat-chip" data-cat="${escapeHtml(c.name)}">${escapeHtml(c.name)} <small>(${c.count})</small></span>`
        )
        .join("");

      // Click handler for chips
      categoryChips.querySelectorAll(".cat-chip").forEach((chip) => {
        chip.addEventListener("click", () => {
          chip.classList.toggle("selected");
          const cat = chip.dataset.cat;
          if (selectedCategories.includes(cat)) {
            selectedCategories = selectedCategories.filter((c) => c !== cat);
          } else {
            selectedCategories.push(cat);
          }
        });
      });
    } else {
      categoryChips.innerHTML = '<span class="loading-text">No categories found</span>';
    }
  } catch {
    categoryChips.innerHTML = '<span class="loading-text">Failed to load categories</span>';
  }
}

// ─── Load year range ────────────────────────────────────────────────────────
async function loadYears() {
  try {
    const resp = await fetch(`${API_BASE}/api/years`);
    const data = await resp.json();
    yearMinInput.value = data.min;
    yearMaxInput.value = data.max;
    yearMinInput.min = data.min;
    yearMaxInput.max = data.max;
  } catch {
    // Use defaults
  }
}

// ─── Load stats ─────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const resp = await fetch(`${API_BASE}/api/stats`);
    const data = await resp.json();
    const docCount = document.getElementById("doc-count");
    docCount.textContent = `Hybrid search over ${data.documents.toLocaleString()} arXiv CS papers — BM25 + kNN + RRF`;
  } catch {
    // Ignore
  }
}

// ─── Utils ──────────────────────────────────────────────────────────────────
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
