"""Background job worker thread."""

from __future__ import annotations

from threading import Event

from PySide6.QtCore import QThread, Signal

from deepmeerkat.config import JobConfig
from deepmeerkat.runner import run_job


class JobThread(QThread):
    finished_ok = Signal(list)
    failed = Signal(str)
    progress = Signal(float, str)

    def __init__(self, config: JobConfig) -> None:
        super().__init__()
        self._config = config
        self._cancel = Event()

    def run(self) -> None:
        try:
            paths = run_job(
                self._config,
                progress=lambda p, m: self.progress.emit(p, m),
                cancel=self._cancel,
            )
            self.finished_ok.emit([str(p) for p in paths])
        except Exception as e:
            self.failed.emit(str(e))

    def request_cancel(self) -> None:
        self._cancel.set()
