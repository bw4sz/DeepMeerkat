"""Main application window (MegaDetector-first)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from deepmeerkat.config import (
    DetectionMode,
    FishDetectorSettings,
    JobConfig,
    MegaDetectorSettings,
    MotionSettings,
)
from deepmeerkat.result_paths import paths_from_result_run_folder
from deepmeerkat.ui.preview import first_video_in_folder, pixmap_from_video_first_frame
from deepmeerkat.ui.resources import logo_png_bytes
from deepmeerkat.ui.review_dialog import ReviewDialog
from deepmeerkat.ui.worker import JobThread

_VIDEO_SUFFIXES = {".mp4", ".avi", ".mov", ".mkv", ".m4v", ".tlv"}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DeepMeerkat 3.0")
        self.resize(800, 720)

        self._thread: JobThread | None = None
        self._last_output_dirs: list[Path] = []

        icon_pix = QPixmap()
        if icon_pix.loadFromData(logo_png_bytes()):
            self.setWindowIcon(QIcon(icon_pix))

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        act_review = file_menu.addAction("Review results folder…")
        act_review.triggered.connect(self._menu_review_folder)
        act_open_result = file_menu.addAction("Open result folder…")
        act_open_result.triggered.connect(self._menu_open_result_folder)
        self._act_reopen_last = file_menu.addAction("Reopen last results")
        self._act_reopen_last.triggered.connect(self._menu_reopen_last)
        self._act_reopen_last.setEnabled(False)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Branding + first-frame preview
        header = QHBoxLayout()
        logo_lbl = QLabel()
        logo_px = QPixmap()
        logo_px.loadFromData(logo_png_bytes())
        if not logo_px.isNull():
            logo_lbl.setPixmap(
                logo_px.scaledToHeight(
                    76,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        logo_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        title_col = QVBoxLayout()
        title = QLabel("DeepMeerkat")
        title.setObjectName("HeaderTitle")
        subtitle = QLabel("Ecological video review · MegaDetector · fish detector · classic motion")
        subtitle.setObjectName("HeaderSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        title_col.addStretch()

        preview_wrap = QVBoxLayout()
        preview_caption = QLabel("First frame preview")
        preview_caption.setObjectName("PreviewCaption")
        self._preview_label = QLabel()
        self._preview_label.setMinimumSize(340, 192)
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setStyleSheet(
            "background-color: palette(alternate-base); border-radius: 10px; padding: 8px;"
        )
        self._preview_label.setText("Choose a video file to preview")
        self._preview_label.setWordWrap(True)
        preview_wrap.addWidget(preview_caption)
        preview_wrap.addWidget(self._preview_label)

        header.addWidget(logo_lbl, alignment=Qt.AlignmentFlag.AlignTop)
        header.addLayout(title_col, stretch=1)
        header.addLayout(preview_wrap)
        layout.addLayout(header)

        # Input / output
        io_box = QGroupBox("Input / output")
        io_form = QFormLayout()
        self.input_edit = QLineEdit()
        self.input_edit.textChanged.connect(self._refresh_preview)
        self.output_edit = QLineEdit()
        in_row = QHBoxLayout()
        in_row.addWidget(self.input_edit)
        btn_in_file = QPushButton("Video file…")
        btn_in_file.clicked.connect(self._browse_input_file)
        btn_in_dir = QPushButton("Folder…")
        btn_in_dir.clicked.connect(self._browse_input_folder)
        in_row.addWidget(btn_in_file)
        in_row.addWidget(btn_in_dir)
        iw = QWidget()
        iw.setLayout(in_row)
        out_row = QHBoxLayout()
        out_row.addWidget(self.output_edit)
        btn_out = QPushButton("Browse…")
        btn_out.clicked.connect(self._browse_output)
        out_row.addWidget(btn_out)
        ow = QWidget()
        ow.setLayout(out_row)
        io_form.addRow("Input (file or folder)", iw)
        io_form.addRow("Output folder", ow)
        io_box.setLayout(io_form)
        layout.addWidget(io_box)

        # Mode
        mode_box = QGroupBox("Mode")
        mode_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("MegaDetector (recommended)", DetectionMode.MEGADETECTOR)
        self.mode_combo.addItem("Community Fish Detector (underwater)", DetectionMode.FISH)
        self.mode_combo.addItem("Classic motion (OpenCV)", DetectionMode.MOTION)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(QLabel("Detection:"))
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        mode_box.setLayout(mode_layout)
        layout.addWidget(mode_box)

        # MegaDetector options
        self.md_group = QGroupBox("MegaDetector options")
        md_form = QFormLayout()
        self.md_model = QLineEdit("MDV5A")
        self.md_conf = QDoubleSpinBox()
        self.md_conf.setRange(0.0, 1.0)
        self.md_conf.setSingleStep(0.05)
        self.md_conf.setValue(0.25)
        self.md_stride = QSpinBox()
        self.md_stride.setRange(1, 1000)
        self.md_stride.setValue(1)
        self.md_target_fps = QDoubleSpinBox()
        self.md_target_fps.setRange(0.0, 120.0)
        self.md_target_fps.setSpecialValueText("off")
        self.md_target_fps.setValue(0.0)
        self.md_max_dim = QSpinBox()
        self.md_max_dim.setRange(0, 8000)
        self.md_max_dim.setValue(1280)
        self.md_max_dim.setSpecialValueText("full")
        self.md_json = QCheckBox("Write megadetector_results.json")
        self.md_json.setChecked(True)
        self.md_save_frames = QCheckBox(
            "Save JPEG frames for frames with detections (detection_frames/)"
        )
        self.md_save_frames.setChecked(False)
        md_form.addRow("Model", self.md_model)
        md_form.addRow("Min confidence", self.md_conf)
        md_form.addRow("Frame stride", self.md_stride)
        md_form.addRow("Target FPS cap (0=off)", self.md_target_fps)
        md_form.addRow("Max dimension (0=full)", self.md_max_dim)
        md_form.addRow(self.md_json)
        md_form.addRow(self.md_save_frames)
        self.md_group.setLayout(md_form)
        layout.addWidget(self.md_group)

        # Community Fish Detector (RF-DETR)
        self.fish_group = QGroupBox("Community Fish Detector (RF-DETR)")
        fish_form = QFormLayout()
        fw_row = QHBoxLayout()
        self.fish_weights_edit = QLineEdit()
        self.fish_weights_edit.setPlaceholderText(
            "Optional: path to .pth — leave blank to download automatically (~116 MB, once)"
        )
        btn_fw = QPushButton("Weights file…")
        btn_fw.clicked.connect(self._browse_fish_weights)
        fw_row.addWidget(self.fish_weights_edit)
        fw_row.addWidget(btn_fw)
        fw_w = QWidget()
        fw_w.setLayout(fw_row)
        self.fish_conf = QDoubleSpinBox()
        self.fish_conf.setRange(0.0, 1.0)
        self.fish_conf.setSingleStep(0.05)
        self.fish_conf.setValue(0.3)
        self.fish_resolution = QSpinBox()
        self.fish_resolution.setRange(320, 1280)
        self.fish_resolution.setValue(640)
        self.fish_stride = QSpinBox()
        self.fish_stride.setRange(1, 1000)
        self.fish_stride.setValue(1)
        self.fish_target_fps = QDoubleSpinBox()
        self.fish_target_fps.setRange(0.0, 120.0)
        self.fish_target_fps.setSpecialValueText("off")
        self.fish_target_fps.setValue(0.0)
        self.fish_max_dim = QSpinBox()
        self.fish_max_dim.setRange(0, 8000)
        self.fish_max_dim.setValue(1280)
        self.fish_max_dim.setSpecialValueText("full")
        self.fish_json = QCheckBox("Write fish_results.json")
        self.fish_json.setChecked(True)
        self.fish_save_frames = QCheckBox(
            "Save JPEG frames for frames with detections (detection_frames/)"
        )
        self.fish_save_frames.setChecked(False)
        fish_form.addRow("Weights (.pth, optional)", fw_w)
        fish_form.addRow("Min confidence", self.fish_conf)
        fish_form.addRow("RF-DETR resolution", self.fish_resolution)
        fish_form.addRow("Frame stride", self.fish_stride)
        fish_form.addRow("Target FPS cap (0=off)", self.fish_target_fps)
        fish_form.addRow("Max dimension (0=full)", self.fish_max_dim)
        fish_form.addRow(self.fish_json)
        fish_form.addRow(self.fish_save_frames)
        self.fish_group.setLayout(fish_form)
        layout.addWidget(self.fish_group)

        # Motion options (secondary)
        self.motion_group = QGroupBox("Classic motion (OpenCV)")
        mo_form = QFormLayout()
        self.mog_lr = QDoubleSpinBox()
        self.mog_lr.setRange(0.001, 1.0)
        self.mog_lr.setValue(0.1)
        self.mog_var = QSpinBox()
        self.mog_var.setRange(1, 200)
        self.mog_var.setValue(20)
        self.min_area = QDoubleSpinBox()
        self.min_area.setRange(0.0001, 1.0)
        self.min_area.setDecimals(4)
        self.min_area.setValue(0.01)
        self.motion_knn = QCheckBox("Use KNN subtractor")
        self.training = QCheckBox("Training mode (export motion crops only)")
        mo_form.addRow("MOG learning rate", self.mog_lr)
        mo_form.addRow("MOG variance", self.mog_var)
        mo_form.addRow("Min area (fraction of frame)", self.min_area)
        mo_form.addRow(self.motion_knn)
        mo_form.addRow(self.training)
        self.motion_group.setLayout(mo_form)
        self.motion_group.setVisible(False)
        layout.addWidget(self.motion_group)

        # ROI
        roi_box = QGroupBox("Optional ROI (x, y, width, height)")
        roi_layout = QHBoxLayout()
        self.roi_x = QSpinBox()
        self.roi_y = QSpinBox()
        self.roi_w = QSpinBox()
        self.roi_h = QSpinBox()
        for s in (self.roi_x, self.roi_y, self.roi_w, self.roi_h):
            s.setRange(0, 20000)
        roi_layout.addWidget(QLabel("x"))
        roi_layout.addWidget(self.roi_x)
        roi_layout.addWidget(QLabel("y"))
        roi_layout.addWidget(self.roi_y)
        roi_layout.addWidget(QLabel("w"))
        roi_layout.addWidget(self.roi_w)
        roi_layout.addWidget(QLabel("h"))
        roi_layout.addWidget(self.roi_h)
        self.roi_enable = QCheckBox("Enable ROI")
        roi_layout.addWidget(self.roi_enable)
        roi_box.setLayout(roi_layout)
        layout.addWidget(roi_box)

        # Run
        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self._run)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

        self.progress_label = QLabel("")
        layout.addWidget(self.progress_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(180)
        layout.addWidget(self.log)

        self._on_mode_changed()
        self._refresh_preview()

    def _preview_video_path(self) -> Path | None:
        text = self.input_edit.text().strip()
        if not text:
            return None
        p = Path(text)
        if p.is_file() and p.suffix.lower() in _VIDEO_SUFFIXES:
            return p
        if p.is_dir():
            return first_video_in_folder(p)
        return None

    def _refresh_preview(self) -> None:
        vp = self._preview_video_path()
        if vp is None:
            self._preview_label.clear()
            text = self.input_edit.text().strip()
            if not text:
                self._preview_label.setText("Choose a video file to preview")
            elif Path(text).is_dir():
                self._preview_label.setText(
                    "No video files found in folder, or pick a single video file."
                )
            else:
                self._preview_label.setText(
                    "Select a supported video file to preview the first frame."
                )
            return
        pm = pixmap_from_video_first_frame(vp)
        if pm is None or pm.isNull():
            self._preview_label.clear()
            self._preview_label.setText("Could not read the first frame from this file.")
            return
        self._preview_label.setText("")
        self._preview_label.setPixmap(pm)

    def _on_mode_changed(self) -> None:
        mode = self.mode_combo.currentData()
        self.md_group.setVisible(mode == DetectionMode.MEGADETECTOR)
        self.fish_group.setVisible(mode == DetectionMode.FISH)
        self.motion_group.setVisible(mode == DetectionMode.MOTION)

    def _browse_input_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Video file",
            str(Path.home()),
            "Video (*.mp4 *.avi *.mov *.mkv);;All (*.*)",
        )
        if path:
            self.input_edit.setText(path)

    def _browse_input_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Folder with videos", str(Path.home()))
        if d:
            self.input_edit.setText(d)

    def _browse_output(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Output folder", str(Path.home()))
        if d:
            self.output_edit.setText(d)

    def _menu_review_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(
            self,
            "Result folder (contains annotations.csv)",
            str(Path.home()),
        )
        if d:
            ReviewDialog(Path(d), self).exec()

    def _browse_fish_weights(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Fish detector weights (.pth)",
            str(Path.home()),
            "PyTorch weights (*.pth);;All (*.*)",
        )
        if path:
            self.fish_weights_edit.setText(path)

    def _menu_open_result_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(
            self,
            "Result folder (contains annotations.csv)",
            str(Path.home()),
        )
        if not d:
            return
        video, out_parent = paths_from_result_run_folder(Path(d))
        if out_parent is None:
            QMessageBox.warning(
                self,
                "DeepMeerkat",
                "That folder does not contain annotations.csv.",
            )
            return
        if video is not None:
            self.input_edit.setText(str(video))
        self.output_edit.setText(str(out_parent))
        QMessageBox.information(
            self,
            "DeepMeerkat",
            "Loaded input video and output folder from the result directory.\n"
            "Use “Review results folder…” or run again after changing settings.",
        )

    def _menu_reopen_last(self) -> None:
        if not self._last_output_dirs:
            return
        ReviewDialog(self._last_output_dirs[0], self).exec()

    def _build_config(self) -> JobConfig:
        inp = Path(self.input_edit.text().strip())
        out = Path(self.output_edit.text().strip())
        mode: DetectionMode = self.mode_combo.currentData()

        roi: tuple[int, int, int, int] | None = None
        if self.roi_enable.isChecked():
            roi = (self.roi_x.value(), self.roi_y.value(), self.roi_w.value(), self.roi_h.value())

        tgt = self.md_target_fps.value()
        if tgt <= 0:
            tgt = None

        max_d = self.md_max_dim.value()
        if max_d <= 0:
            max_d = 0

        md = MegaDetectorSettings(
            model=self.md_model.text().strip() or "MDV5A",
            confidence_threshold=float(self.md_conf.value()),
            frame_stride=int(self.md_stride.value()),
            target_fps=tgt,
            write_json=self.md_json.isChecked(),
            max_dimension=max_d,
            save_detection_frames=self.md_save_frames.isChecked(),
        )
        ft = self.fish_target_fps.value()
        if ft <= 0:
            ft = None
        fmax = self.fish_max_dim.value()
        if fmax <= 0:
            fmax = 0
        fi = FishDetectorSettings(
            weights_path=self.fish_weights_edit.text().strip(),
            confidence_threshold=float(self.fish_conf.value()),
            resolution=int(self.fish_resolution.value()),
            frame_stride=int(self.fish_stride.value()),
            target_fps=ft,
            write_json=self.fish_json.isChecked(),
            max_dimension=fmax,
            save_detection_frames=self.fish_save_frames.isChecked(),
        )
        mo = MotionSettings(
            mog_learning_rate=float(self.mog_lr.value()),
            mog_variance=int(self.mog_var.value()),
            min_area_fraction=float(self.min_area.value()),
            use_knn=self.motion_knn.isChecked(),
            training_mode=self.training.isChecked(),
        )
        return JobConfig(
            input_path=inp,
            output_dir=out,
            mode=mode,
            megadetector=md,
            motion=mo,
            fish=fi,
            roi=roi,
        )

    def _run(self) -> None:
        if not self.input_edit.text().strip() or not self.output_edit.text().strip():
            QMessageBox.warning(self, "DeepMeerkat", "Please set input and output paths.")
            return
        cfg = self._build_config()
        self.log.clear()
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        self._thread = JobThread(cfg)
        self._thread.progress.connect(self._on_progress)
        self._thread.finished_ok.connect(self._on_done)
        self._thread.failed.connect(self._on_fail)
        self._thread.finished.connect(self._thread_finished)
        self._thread.start()

    def _thread_finished(self) -> None:
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._thread = None

    def _on_progress(self, p: float, msg: str) -> None:
        self.progress_label.setText(f"{p*100:.1f}% — {msg}")
        self.log.append(msg)

    def _on_done(self, paths: list) -> None:
        self.progress_label.setText("Complete.")
        self._last_output_dirs = [Path(p) for p in paths]
        self._act_reopen_last.setEnabled(bool(self._last_output_dirs))
        primary = self._last_output_dirs[0]
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("DeepMeerkat")
        msg.setText("Run finished.")
        msg.setInformativeText("Output:\n" + "\n".join(str(p) for p in self._last_output_dirs))
        btn_open = msg.addButton("Open folder", QMessageBox.ButtonRole.AcceptRole)
        btn_review = msg.addButton("Review detections…", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked == btn_open:
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices

            QDesktopServices.openUrl(QUrl.fromLocalFile(str(primary.resolve())))
        elif clicked == btn_review:
            ReviewDialog(primary, self).exec()

    def _on_fail(self, err: str) -> None:
        QMessageBox.critical(self, "DeepMeerkat", err)
        self.log.append(f"ERROR: {err}")

    def _cancel(self) -> None:
        if self._thread:
            self._thread.request_cancel()
            self.log.append("Cancel requested…")

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread and self._thread.isRunning():
            self._thread.request_cancel()
            self._thread.wait(3000)
        super().closeEvent(event)
