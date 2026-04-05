"""Review run results: scrub video and jump to detection rows."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QImage, QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from deepmeerkat.result_paths import load_annotation_rows, resolve_source_video
from deepmeerkat.ui.review_filters import (
    filter_annotation_rows,
    sorted_unique_frames,
    unique_labels,
)


def _bgr_for_label(name: str) -> tuple[int, int, int]:
    n = name.lower()
    if n == "person":
        return (220, 120, 52)
    if n == "vehicle":
        return (34, 126, 230)
    if n == "fish":
        return (60, 180, 255)
    return (99, 180, 40)


class ReviewDialog(QDialog):
    """Scrub timeline, filter detections, keyboard shortcuts, optional playback."""

    def __init__(self, output_dir: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Review detections — {output_dir.name}")
        self.resize(1040, 680)

        self._output_dir = Path(output_dir)
        self._video_path = resolve_source_video(self._output_dir)
        self._cap: cv2.VideoCapture | None = None
        self._fps = 30.0
        self._total_frames = 1
        self._all_rows = load_annotation_rows(self._output_dir / "annotations.csv")
        self._visible_rows: list[dict[str, str]] = []
        self._detection_frames: list[int] = []
        self._playing = False
        self._play_timer = QTimer(self)

        layout = QVBoxLayout(self)

        if self._video_path is None:
            layout.addWidget(
                QLabel(
                    "Could not find source video. "
                    "Open a result folder from MegaDetector or motion mode with parameters.csv."
                )
            )
            bb = QDialogButtonBox(QDialogButtonBox.Close)
            bb.rejected.connect(self.reject)
            layout.addWidget(bb)
            return

        self._cap = cv2.VideoCapture(str(self._video_path))
        if not self._cap.isOpened():
            layout.addWidget(QLabel(f"Could not open video:\n{self._video_path}"))
            bb = QDialogButtonBox(QDialogButtonBox.Close)
            bb.rejected.connect(self.reject)
            layout.addWidget(bb)
            return

        self._fps = float(self._cap.get(cv2.CAP_PROP_FPS) or 30.0)
        self._total_frames = max(1, int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1))

        self._video_label = QLabel()
        self._video_label.setMinimumSize(480, 270)
        self._video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_label.setStyleSheet("background-color: palette(base);")

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(1)
        self._slider.setMaximum(self._total_frames)
        self._slider.valueChanged.connect(self._on_slider)
        self._slider.sliderPressed.connect(self._stop_playback)

        self._frame_info = QLabel()

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Label:"))
        self._label_combo = QComboBox()
        self._label_combo.addItem("All", None)
        for lab in unique_labels(self._all_rows):
            self._label_combo.addItem(lab, lab)
        self._label_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._label_combo, stretch=1)
        filter_row.addWidget(QLabel("Min score:"))
        self._min_score = QDoubleSpinBox()
        self._min_score.setRange(0.0, 1.0)
        self._min_score.setSingleStep(0.05)
        self._min_score.setDecimals(2)
        self._min_score.setValue(0.0)
        self._min_score.valueChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._min_score)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Frame", "Time", "Label", "Score", "Box"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.currentCellChanged.connect(self._on_table_cell)

        right_panel = QWidget()
        right_col = QVBoxLayout(right_panel)
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.addLayout(filter_row)
        hint = QLabel("Click a row to jump. Drag the splitter to resize.")
        hint.setObjectName("ReviewHint")
        hint.setStyleSheet("color: palette(mid); font-size: 11px;")
        right_col.addWidget(hint)
        right_col.addWidget(self._table)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.addWidget(self._video_label)
        self._splitter.addWidget(right_panel)
        self._splitter.setStretchFactor(0, 2)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([640, 360])
        self._splitter.splitterMoved.connect(self._on_splitter_moved)

        layout.addWidget(self._splitter)
        layout.addWidget(self._slider)
        layout.addWidget(self._frame_info)

        nav = QHBoxLayout()
        self._btn_prev_det = QPushButton("◀ Prev detection")
        self._btn_prev_det.clicked.connect(self._go_prev_detection)
        self._btn_next_det = QPushButton("Next detection ▶")
        self._btn_next_det.clicked.connect(self._go_next_detection)
        nav.addWidget(self._btn_prev_det)
        nav.addWidget(self._btn_next_det)
        nav.addStretch()
        open_btn = QPushButton("Open result folder")
        open_btn.clicked.connect(self._open_folder)
        nav.addWidget(open_btn)
        layout.addLayout(nav)

        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

        self._play_timer.timeout.connect(self._on_play_tick)
        self._install_shortcuts()

        self._apply_filter(rebuild_table=True)
        self._slider.setValue(1)
        self._show_frame(1)

    def _install_shortcuts(self) -> None:
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, activated=lambda: self._nudge_frame(-1))
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, activated=lambda: self._nudge_frame(1))
        QShortcut(QKeySequence(Qt.Key.Key_Home), self, activated=lambda: self._set_frame(1))
        QShortcut(
            QKeySequence(Qt.Key.Key_End),
            self,
            activated=lambda: self._set_frame(self._total_frames),
        )
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, activated=self._toggle_playback)

    def _on_splitter_moved(self, _pos: int, _index: int) -> None:
        self._show_frame(self._slider.value())

    def _on_filter_changed(self, *_args: object) -> None:
        self._apply_filter(rebuild_table=True)
        self._show_frame(self._slider.value())

    def _apply_filter(self, *, rebuild_table: bool) -> None:
        label_data = self._label_combo.currentData()
        label = label_data if isinstance(label_data, str) else None
        if self._label_combo.currentText() == "All":
            label = None
        self._visible_rows = filter_annotation_rows(
            self._all_rows,
            label=label,
            min_score=float(self._min_score.value()),
        )
        self._detection_frames = sorted_unique_frames(self._visible_rows)
        has_det = len(self._detection_frames) > 0
        self._btn_prev_det.setEnabled(has_det)
        self._btn_next_det.setEnabled(has_det)

        if not rebuild_table:
            return

        self._table.blockSignals(True)
        self._table.setRowCount(len(self._visible_rows))
        for i, row in enumerate(self._visible_rows):
            self._table.setItem(i, 0, QTableWidgetItem(str(row.get("frame", ""))))
            self._table.setItem(i, 1, QTableWidgetItem(str(row.get("clock", ""))))
            self._table.setItem(i, 2, QTableWidgetItem(str(row.get("label", ""))))
            self._table.setItem(i, 3, QTableWidgetItem(str(row.get("score", ""))))
            self._table.setItem(
                i,
                4,
                QTableWidgetItem(
                    f"{row.get('x', '')},{row.get('y', '')} "
                    f"{row.get('w', '')}×{row.get('h', '')}"
                ),
            )
        self._table.blockSignals(False)

    def _frame_rows(self, frame_1based: int) -> list[dict[str, str]]:
        return [r for r in self._visible_rows if str(r.get("frame", "")) == str(frame_1based)]

    def _show_frame(self, frame_1based: int) -> None:
        if self._cap is None:
            return
        idx0 = max(0, frame_1based - 1)
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, idx0)
        ret, frame = self._cap.read()
        if not ret or frame is None:
            return
        for r in self._frame_rows(frame_1based):
            try:
                x = int(float(r["x"]))
                y = int(float(r["y"]))
                w = int(float(r["w"]))
                h = int(float(r["h"]))
            except (KeyError, ValueError):
                continue
            lab = str(r.get("label", ""))
            col = _bgr_for_label(lab)
            cv2.rectangle(frame, (x, y), (x + w, y + h), col, 2)
            cv2.putText(
                frame,
                lab,
                (x, max(20, y - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                col,
                2,
                cv2.LINE_AA,
            )
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg.copy())
        self._video_label.setPixmap(
            pix.scaled(
                self._video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        t = (frame_1based - 1) / self._fps if self._fps > 0 else 0.0
        nf = len(self._detection_frames)
        self._frame_info.setText(
            f"Frame {frame_1based} / {self._total_frames}  ·  ~{t:.1f}s  ·  "
            f"{nf} detection row(s) in table  ·  {self._video_path.name}"
        )

    def _set_frame(self, frame_1based: int) -> None:
        self._stop_playback()
        fr = min(max(frame_1based, 1), self._total_frames)
        self._slider.blockSignals(True)
        self._slider.setValue(fr)
        self._slider.blockSignals(False)
        self._show_frame(fr)

    def _nudge_frame(self, delta: int) -> None:
        self._stop_playback()
        self._set_frame(self._slider.value() + delta)

    def _on_slider(self, value: int) -> None:
        self._show_frame(value)

    def _on_table_cell(self, current_row: int, _c: int, _pr: int, _pc: int) -> None:
        if current_row < 0:
            return
        item = self._table.item(current_row, 0)
        if item is None:
            return
        try:
            fr = int(item.text())
        except ValueError:
            return
        self._stop_playback()
        self._slider.blockSignals(True)
        self._slider.setValue(min(max(fr, 1), self._total_frames))
        self._slider.blockSignals(False)
        self._show_frame(fr)

    def _go_next_detection(self) -> None:
        if not self._detection_frames:
            return
        self._stop_playback()
        cur = self._slider.value()
        nxt = None
        for f in self._detection_frames:
            if f > cur:
                nxt = f
                break
        if nxt is None:
            nxt = self._detection_frames[0]
        self._set_frame(nxt)

    def _go_prev_detection(self) -> None:
        if not self._detection_frames:
            return
        self._stop_playback()
        cur = self._slider.value()
        prev = None
        for f in reversed(self._detection_frames):
            if f < cur:
                prev = f
                break
        if prev is None:
            prev = self._detection_frames[-1]
        self._set_frame(prev)

    def _toggle_playback(self) -> None:
        if self._playing:
            self._stop_playback()
        else:
            self._start_playback()

    def _start_playback(self) -> None:
        if self._total_frames <= 1:
            return
        fps = max(min(self._fps, 60.0), 1.0)
        self._play_timer.setInterval(int(round(1000.0 / fps)))
        self._playing = True
        self._play_timer.start()

    def _stop_playback(self) -> None:
        self._playing = False
        self._play_timer.stop()

    def _on_play_tick(self) -> None:
        cur = self._slider.value()
        if cur >= self._total_frames:
            self._stop_playback()
            return
        nxt = cur + 1
        self._slider.blockSignals(True)
        self._slider.setValue(nxt)
        self._slider.blockSignals(False)
        self._show_frame(nxt)
        if nxt >= self._total_frames:
            self._stop_playback()

    def _open_folder(self) -> None:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._output_dir.resolve())))

    def closeEvent(self, event: QCloseEvent) -> None:
        self._stop_playback()
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        super().closeEvent(event)
