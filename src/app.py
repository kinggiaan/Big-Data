"""
Entry-point wrapper kept for backwards compatibility.

The actual Streamlit app lives in `src/ui/app.py`.
Run as before:
  .\venv\Scripts\streamlit.exe run src/app.py
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("src.ui.app", run_name="__main__")
