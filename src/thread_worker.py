import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque, Counter
from PyQt6.QtCore import QThread, pyqtSignal
from src.engine import NeuralEngine
from src.config import CAMERA_ID, FRAME_WIDTH, FRAME_HEIGHT, FPS_LIMIT

class VideoWorker(QThread):
    frame_signal = pyqtSignal(np.ndarray)
    data_signal = pyqtSignal(str, float, str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.mirror = True
        self.light_boost = 1.0
        self.engine = NeuralEngine()
        
        # Буфер для стабилизации ( Majority Voting )
        self.pred_buffer = deque(maxlen=10)
        
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0  # Быстрый режим для 60 FPS
        )
        
        self.mode = "PREDICT"
        self.collect_label = ""
        self.buffer_X = []
        self.buffer_y = []

    def run(self):
        cap = cv2.VideoCapture(CAMERA_ID)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        
        while self.running:
            ret, frame = cap.read()
            if not ret: continue

            if self.mirror:
                frame = cv2.flip(frame, 1)

            # --- 1. LIGHT BOOST (Программная яркость) ---
            if self.light_boost > 1.0:
                frame = cv2.convertScaleAbs(frame, alpha=self.light_boost, beta=10)

            # --- 2. ОБРАБОТКА (Анализ на уменьшенном кадре для скорости) ---
            small_frame = cv2.resize(frame, (640, 360))
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            results = self.holistic.process(rgb_small)
            
            # --- 3. ЭКСТРАКЦИЯ С НОРМАЛИЗАЦИЕЙ ---
            # Используем метод нормализации из engine
            l_hand = self.engine.normalize_hand(results.left_hand_landmarks)
            r_hand = self.engine.normalize_hand(results.right_hand_landmarks)
            features = l_hand + r_hand

            status_text = "..."
            conf = 0.0
            
            # --- 4. ЛОГИКА ---
            if any(v != 0 for v in features):
                if self.mode == "COLLECT" and self.collect_label:
                    self.buffer_X.append(features)
                    self.buffer_y.append(self.collect_label)
                    cv2.circle(frame, (40, 40), 15, (0, 0, 255), -1)
                    status_text = f"REC: {len(self.buffer_X)}"
                
                elif self.mode == "PREDICT":
                    res_label, res_conf = self.engine.predict(features)
                    
                    # Стабилизация через буфер
                    if res_conf > 0.65:
                        self.pred_buffer.append(res_label)
                    else:
                        self.pred_buffer.append("...")
                    
                    if len(self.pred_buffer) > 0:
                        counts = Counter(self.pred_buffer)
                        status_text, count = counts.most_common(1)[0]
                        conf = res_conf
            else:
                self.pred_buffer.append("...")

            # --- 5. ОТРИСОВКА ---
            self.draw_beautiful_skeleton(frame, results)

            self.frame_signal.emit(frame)
            self.data_signal.emit(status_text, conf, self.mode)
            
            # Frame pacing (60 FPS)
            time.sleep(1/FPS_LIMIT)
            
        cap.release()

    def draw_beautiful_skeleton(self, image, results):
        """Неоновая отрисовка скелета"""
        h, w, _ = image.shape
        def draw_side(landmarks, color_line, color_dot):
            if not landmarks: return
            pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]
            for s, e in self.mp_holistic.HAND_CONNECTIONS:
                cv2.line(image, pts[s], pts[e], (0, 0, 0), 3)
                cv2.line(image, pts[s], pts[e], color_line, 1, cv2.LINE_AA)
            for p in pts:
                cv2.circle(image, p, 3, color_dot, -1)

        draw_side(results.left_hand_landmarks, (255, 0, 127), (255, 255, 255))
        draw_side(results.right_hand_landmarks, (0, 229, 255), (255, 255, 255))

    def start_collect(self, label):
        self.mode = "COLLECT"
        self.collect_label = label
    
    def stop_collect(self):
        self.mode = "PREDICT"
        self.collect_label = ""

    def save_data(self):
        count = self.engine.save_dataset(self.buffer_X, self.buffer_y)
        self.buffer_X, self.buffer_y = [], []
        return count

    def train_model(self):
        return self.engine.train()

    def stop(self):
        self.running = False
        self.wait()