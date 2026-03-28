"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/search/search_compare.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.search.search_compare", run_name="__main__")
