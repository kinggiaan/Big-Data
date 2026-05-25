"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/pipeline/setup_dual_index.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.pipeline.setup_dual_index", run_name="__main__")
