"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/evaluation/benchmark_multiscale.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.evaluation.benchmark_multiscale", run_name="__main__")

