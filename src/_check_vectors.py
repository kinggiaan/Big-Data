"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/utils/_check_vectors.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.utils._check_vectors", run_name="__main__")

