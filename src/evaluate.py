"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/evaluation/evaluate.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.evaluation.evaluate", run_name="__main__")

