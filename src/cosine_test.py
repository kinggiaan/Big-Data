"""
Entry-point wrapper kept for backwards compatibility.

Implementation moved to: `src/utils/cosine_test.py`
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.utils.cosine_test", run_name="__main__")

