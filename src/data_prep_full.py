"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/pipeline/data_prep_full.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.pipeline.data_prep_full", run_name="__main__")
