"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/evaluation/collect_benchmark_100k.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.evaluation.collect_benchmark_100k", run_name="__main__")

