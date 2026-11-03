"""Aegis Health desktop launcher."""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


def main() -> int:
    import customtkinter as ctk

    from aegis.app import AegisApp

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = AegisApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
