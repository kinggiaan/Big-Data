"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/utils/truncate_jsonl.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.utils.truncate_jsonl", run_name="__main__")

