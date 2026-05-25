r"""
Entry-point wrapper kept for backwards compatibility.

The actual Streamlit app lives in `src/ui/app.py`.
Run as before:
  .\venv\Scripts\streamlit.exe run src/app.py
"""

import os
import sys

# Project root (parent of `src/`) so `import src...` works without PYTHONPATH.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import runpy

if __name__ == "__main__":
    runpy.run_module("src.ui.app", run_name="__main__")
