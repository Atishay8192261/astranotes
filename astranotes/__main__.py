"""AstraNotes entry point: python -m astranotes

Launches the CustomTkinter GUI (the 3-tier presentation frontend). If the
Python build has no Tk support, prints the one command needed to fix it
rather than crashing with a bare ImportError.
"""

from __future__ import annotations

import sys


def main() -> None:
    try:
        from astranotes.gui.app import main as gui_main
    except ImportError as exc:
        if "_tkinter" in str(exc) or "tkinter" in str(exc).lower():
            print(
                "AstraNotes needs Tk support to show its GUI.\n"
                "This Python build has no _tkinter. Install Tk, then retry:\n"
                "  brew install python-tk@3.11\n"
                "(or use a Python built with Tcl/Tk).",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc
        raise

    try:
        gui_main()
    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
