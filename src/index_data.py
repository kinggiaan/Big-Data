"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/pipeline/index_data.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.pipeline.index_data", run_name="__main__")
