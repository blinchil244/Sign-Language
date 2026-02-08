# src/main_window.py
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QGroupBox, 
                             QTextEdit, QProgressBar, QTabWidget, QComboBox, 
                             QCheckBox, QApplication, QInputDialog, QMessageBox, QSlider)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from src.thread_worker import VideoWorker
from src.config import TRANSLATIONS

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang_code = "RU"
        self.worker = None
        
        self.resize(1300, 900)
        self.load_css()
        self.build_ui()
        self.start_camera()

    def load_css(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "ui_style.qss")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def build_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)

        # --- HEADER ---
        top_bar = QHBoxLayout()
        self.title_lbl = QLabel("NEURAL GESTURE PRO")
        self.title_lbl.setStyleSheet("font-size: 22px; font-weight: 900; color: #00E5FF;")
        
        self.lang_box = QComboBox()
        self.lang_box.addItems(["RU", "KZ", "EN"])
        self.lang_box.currentTextChanged.connect(self.set_language)
        
        top_bar.addWidget(self.title_lbl)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("LNG:"))
        top_bar.addWidget(self.lang_box)
        self.main_layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Табы
        self.init_main_tab()
        self.init_settings_tab()
        
        self.update_texts()

    def init_main_tab(self):
        self.tab_main = QWidget()
        layout = QHBoxLayout(self.tab_main)
        
        left_col = QVBoxLayout()
        self.grp_cam = QGroupBox("CAM")
        cam_layout = QVBoxLayout()
        
        self.video_lbl = QLabel()
        self.video_lbl.setFixedSize(850, 600)
        self.video_lbl.setStyleSheet("background: #000; border-radius: 10px;")
        
        self.res_lbl = QLabel("READY")
        self.res_lbl.setObjectName("Result")
        self.res_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.res_lbl.setFixedHeight(80)
        
        self.conf_bar = QProgressBar()
        self.conf_bar.setFixedHeight(12)
        
        cam_layout.addWidget(self.video_lbl)
        cam_layout.addWidget(self.conf_bar)
        cam_layout.addWidget(self.res_lbl)
        self.grp_cam.setLayout(cam_layout)
        left_col.addWidget(self.grp_cam)
        
        right_col = QVBoxLayout()
        self.grp_ctrl = QGroupBox("CTRL")
        ctrl_layout = QVBoxLayout()

        self.input_lbl = QLabel("Label:")
        self.input_field = QLineEdit()
        
        self.btn_rec = QPushButton("RECORD")
        self.btn_rec.setObjectName("RecBtn")
        self.btn_rec.setCheckable(True)
        self.btn_rec.clicked.connect(self.on_record_toggle)
        
        self.btn_save = QPushButton("SAVE")
        self.btn_save.clicked.connect(self.on_save)
        
        self.btn_train = QPushButton("TRAIN")
        self.btn_train.clicked.connect(self.on_train)
        
        self.btn_delete = QPushButton("DELETE")
        self.btn_delete.setStyleSheet("color: #FF1744;")
        self.btn_delete.clicked.connect(self.on_delete_gesture)
        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        
        ctrl_layout.addWidget(self.input_lbl)
        ctrl_layout.addWidget(self.input_field)
        ctrl_layout.addWidget(self.btn_rec)
        ctrl_layout.addWidget(self.btn_save)
        ctrl_layout.addWidget(self.btn_train)
        ctrl_layout.addWidget(self.btn_delete)
        ctrl_layout.addWidget(self.log_box)
        self.grp_ctrl.setLayout(ctrl_layout)
        right_col.addWidget(self.grp_ctrl)
        
        layout.addLayout(left_col, 70)
        layout.addLayout(right_col, 30)
        self.tabs.addTab(self.tab_main, "TERMINAL")

    def init_settings_tab(self):
        self.tab_sett = QWidget()
        layout = QVBoxLayout(self.tab_sett)
        
        self.chk_mirror = QCheckBox("Mirror Mode")
        self.chk_mirror.setChecked(True)
        self.chk_mirror.stateChanged.connect(self.on_mirror_change)
        
        layout.addWidget(self.chk_mirror)
        
        layout.addWidget(QLabel("LIGHT BOOST:"))
        self.boost_slider = QSlider(Qt.Orientation.Horizontal)
        self.boost_slider.setRange(10, 40)
        self.boost_slider.setValue(10)
        self.boost_slider.valueChanged.connect(self.on_boost_change)
        layout.addWidget(self.boost_slider)
        
        layout.addStretch()
        self.tabs.addTab(self.tab_sett, "SETTINGS")

    def update_texts(self):
        """МГНОВЕННЫЙ ПЕРЕВОД ВСЕГО UI"""
        t = TRANSLATIONS.get(self.lang_code, TRANSLATIONS["RU"])
        self.setWindowTitle(t["window_title"])
        self.grp_cam.setTitle(t["grp_camera"])
        self.grp_ctrl.setTitle(t["grp_control"])
        self.input_lbl.setText(t["lbl_input"])
        self.btn_save.setText(t["btn_save"])
        self.btn_train.setText(t.get("btn_train", "TRAIN")) # На случай если нет в конфиге
        self.chk_mirror.setText(t["lbl_mirror"])
        
        if self.btn_rec.isChecked():
            self.btn_rec.setText(t["btn_record_release"])
        else:
            self.btn_rec.setText(t["btn_record_hold"])
        
        self.tabs.setTabText(0, t.get("tab_main", "TERMINAL"))
        self.tabs.setTabText(1, t.get("tab_settings", "SETTINGS"))

    def start_camera(self):
        self.worker = VideoWorker()
        self.worker.frame_signal.connect(self.draw_frame)
        self.worker.data_signal.connect(self.update_data)
        self.worker.start()

    def set_language(self, lang):
        self.lang_code = lang
        self.update_texts()
        self.log(f"Language: {lang}")

    def on_boost_change(self, val):
        self.worker.light_boost = val / 10.0

    def on_record_toggle(self):
        t = TRANSLATIONS[self.lang_code]
        is_rec = self.btn_rec.isChecked()
        name = self.input_field.text().strip()
        
        if is_rec and not name:
            self.btn_rec.setChecked(False)
            return

        self.btn_rec.setProperty("recording", str(is_rec).lower())
        self.btn_rec.style().unpolish(self.btn_rec)
        self.btn_rec.style().polish(self.btn_rec)
        
        if is_rec:
            self.worker.start_collect(name)
            self.btn_rec.setText(t["btn_record_release"])
        else:
            self.worker.stop_collect()
            self.btn_rec.setText(t["btn_record_hold"])

    def on_save(self):
        cnt = self.worker.save_data()
        self.log(f"Saved: +{cnt}")

    def on_train(self):
        self.log("Training...")
        QApplication.processEvents()
        ok, msg = self.worker.train_model()
        self.log(f"Result: {msg}")

    def on_delete_gesture(self):
        label, ok = QInputDialog.getText(self, "Delete", "Gesture Name:")
        if ok and label:
            success, msg = self.worker.engine.remove_label(label)
            QMessageBox.information(self, "Status", msg)

    def on_mirror_change(self, state):
        self.worker.mirror = (state == 2)

    @pyqtSlot(np.ndarray)
    def draw_frame(self, frame):
        h, w, ch = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.video_lbl.setPixmap(QPixmap.fromImage(qt_img).scaled(850, 600, Qt.AspectRatioMode.KeepAspectRatio))

    @pyqtSlot(str, float, str)
    def update_data(self, text, conf, mode):
        t = TRANSLATIONS[self.lang_code]
        if mode == "COLLECT":
            self.res_lbl.setText(text)
            self.res_lbl.setStyleSheet("color: #FF1744; border: 2px solid #FF1744;")
        else:
            if text == "..." or conf < 0.6:
                self.res_lbl.setText(t["status_ready"])
                self.res_lbl.setStyleSheet("color: #444; border: 2px solid #222;")
                self.conf_bar.setValue(0)
            else:
                self.res_lbl.setText(f"{text.upper()} ({int(conf*100)}%)")
                self.res_lbl.setStyleSheet("color: #00E5FF; border: 2px solid #00E5FF;")
                self.conf_bar.setValue(int(conf * 100))

    def log(self, text):
        self.log_box.append(f">> {text}")

    def closeEvent(self, event):
        self.worker.stop()
        event.accept()