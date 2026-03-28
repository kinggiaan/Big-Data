"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/pipeline/data_prep.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.pipeline.data_prep", run_name="__main__")
