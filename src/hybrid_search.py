"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/search/hybrid_search.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.search.hybrid_search", run_name="__main__")
