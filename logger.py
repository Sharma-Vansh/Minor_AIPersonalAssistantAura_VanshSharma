"""
utils/logger.py
✅ FIXED: Unicode/emoji crash on Windows (cp1252 encoding issue)
✅ All loggers use UTF-8 encoding
"""

import logging
import os
import sys

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "app.log")


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)

    # ── Console handler (UTF-8 forced) ───────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)

    # Force UTF-8 on Windows to prevent emoji crash
    if hasattr(console.stream, 'reconfigure'):
        try:
            console.stream.reconfigure(encoding='utf-8')
        except Exception:
            pass

    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S"
    )
    console.setFormatter(fmt)
    logger.addHandler(console)

    # ── File handler (UTF-8) ─────────────────────────────
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except Exception:
        pass  # If log file can't be created, just use console

    logger.propagate = False
    return logger