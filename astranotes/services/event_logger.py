"""Action event logger — records every UI interaction to prove backend workflow (prof req).

Writes JSON-lines to ~/.astranotes/events.log so graders can see the full
click → controller → service → storage pipeline.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class EventLogger:
    def __init__(self, log_path: Path | None = None) -> None:
        if log_path is None:
            from astranotes.config import resolve_data_dir
            data_dir = Path(resolve_data_dir())
            log_path = data_dir.parent / "events.log"
        self.log_path = log_path
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    def log(self, action: str, detail: str = "") -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "detail": detail,
        }
        try:
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except OSError as exc:
            logger.warning("EventLogger write failed: %s", exc)
        logger.debug("EVENT %s: %s", action, detail)
