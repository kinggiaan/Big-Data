import React, { useState, useEffect } from 'react';
import { searchPapers, getStats, getCategories, getYears } from './api';

function App() {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('hybrid');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState({ total: 0, latency_ms: 0 });
  const [globalStats, setGlobalStats] = useState({ documents: 0 });
  
  // Filter states
  const [availableCategories, setAvailableCategories] = useState([]);
  const [yearRange, setYearRange] = useState({ min: 1990, max: 2026 });
  const [selectedYearMin, setSelectedYearMin] = useState('');
  const [selectedYearMax, setSelectedYearMax] = useState('');
  const [selectedCategories, setSelectedCategories] = useState([]);

  useEffect(() => {
    getStats().then(setGlobalStats).catch(console.error);
    getCategories().then(data => setAvailableCategories(data.categories || [])).catch(console.error);
    getYears().then(data => {
      setYearRange({ min: data.min, max: data.max });
      setSelectedYearMin(data.min);
      setSelectedYearMax(data.max);
    }).catch(console.error);
  }, []);

  const toggleCategory = (catName) => {
    setSelectedCategories(prev => 
      prev.includes(catName) 
        ? prev.filter(c => c !== catName)
        : [...prev, catName]
    );
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    let finalMin = selectedYearMin;
    let finalMax = selectedYearMax;

    // Common sense logic: swap if min > max
    if (finalMin && finalMax && parseInt(finalMin) > parseInt(finalMax)) {
      const temp = finalMin;
      finalMin = finalMax;
      finalMax = temp;
      setSelectedYearMin(finalMin);
      setSelectedYearMax(finalMax);
    }

    setIsLoading(true);
    try {
      const filters = {
        yearMin: finalMin,
        yearMax: finalMax,
        categories: selectedCategories
      };
      const data = await searchPapers(query, mode, 10, filters);
      setResults(data.hits || []);
      setStats({ total: data.total || 0, latency_ms: data.latency_ms || 0 });
    } catch (error) {
      console.error(error);
      alert('Error searching papers. Is the local FastAPI server running?');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1 className="logo-title">🔬 Academic Paper Search</h1>
        <p className="subtitle">
          {globalStats.total_documents > 0 
            ? `Dual-Index Hybrid Search over ${globalStats.total_documents.toLocaleString()} arXiv CS papers` 
            : 'Dual-Index Search — BM25 + kNN + RRF'}
        </p>
      </header>

      <div className="search-container">
        <form className="search-box" onSubmit={handleSearch}>
          <input
            type="text"
            className="search-input"
            placeholder="Search papers... e.g. efficient attention mechanism"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="search-btn">
            🔍
          </button>
        </form>

        <div className="controls-bar">
          <div className="mode-toggle">
            <button
              className={`mode-btn ${mode === 'hybrid' ? 'active' : ''}`}
              onClick={() => setMode('hybrid')}
              type="button"
            >
              ⚡ Hybrid (RRF)
            </button>
            <button
              className={`mode-btn ${mode === 'bm25' ? 'active' : ''}`}
              onClick={() => setMode('bm25')}
              type="button"
            >
              📝 Keyword Search
            </button>
            <button
              className={`mode-btn ${mode === 'knn' ? 'active' : ''}`}
              onClick={() => setMode('knn')}
              type="button"
            >
              🧠 Semantic Search
            </button>
          </div>
          
        </div>
        
        <div className="filters-panel">
          <div className="filter-group">
            <label>Year Range:</label>
            <div className="year-inputs">
              <input 
                type="number" 
                min={yearRange.min} 
                max={yearRange.max} 
                value={selectedYearMin} 
                onChange={e => setSelectedYearMin(e.target.value)} 
              />
              <span>to</span>
              <input 
                type="number" 
                min={yearRange.min} 
                max={yearRange.max} 
                value={selectedYearMax} 
                onChange={e => setSelectedYearMax(e.target.value)} 
              />
            </div>
          </div>
          
          <div className="filter-group">
            <label>Categories:</label>
            <div className="category-chips">
              {availableCategories.map(cat => (
                <span 
                  key={cat.name} 
                  className={`cat-chip ${selectedCategories.includes(cat.name) ? 'selected' : ''}`}
                  onClick={() => toggleCategory(cat.name)}
                >
                  {cat.name} <small>({cat.count})</small>
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {(stats.total > 0 || isLoading) && (
        <div className="stats-bar">
          <div className="stat-item">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Results</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{stats.latency_ms}ms</span>
            <span className="stat-label">Latency</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">
              {mode === 'hybrid' ? 'Hybrid' : mode === 'bm25' ? 'Keyword' : 'Semantic'}
            </span>
            <span className="stat-label">Mode</span>
          </div>
        </div>
      )}

      <div className="results-grid">
        {isLoading && (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        )}

        {!isLoading && results.map((hit, i) => (
          <div className="result-card" key={hit.id || i} style={{ animationDelay: `${i * 50}ms` }}>
            <div className="result-header">
              <h3 className="result-title">
                {i + 1}. {hit.title}
              </h3>
              <span className="result-score">{hit.score.toFixed(4)}</span>
            </div>
            
            <div className="result-meta">
              <span className="meta-item">👤 {hit.authors}</span>
              <span className="meta-item">📅 {hit.year}</span>
              <span className="meta-item">🆔 {hit.id}</span>
            </div>
            
            <p className="result-abstract">{hit.abstract.substring(0, 300)}...</p>
            
            <div className="result-tags">
              {hit.categories && hit.categories.map(cat => (
                <span key={cat} className="tag">{cat}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
