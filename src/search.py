"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/search/search.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.search.search", run_name="__main__")
