"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/pipeline/embed_data.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.pipeline.embed_data", run_name="__main__")
