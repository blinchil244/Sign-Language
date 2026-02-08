# src/engine.py
import os
import shutil
import numpy as np
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

class NeuralEngine:
    """
    Класс отвечает за 'мозги': 
    - Управление данными (.npz)
    - Обучение модели (RandomForest)
    - Предсказания с нормализацией
    """
    def __init__(self):
        # Пути к файлам
        self.base_dir = "data"
        self.data_file = os.path.join(self.base_dir, "words_dataset.npz")
        self.model_file = os.path.join(self.base_dir, "words_model.joblib")
        self.backup_dir = os.path.join(self.base_dir, "backups")
        
        # Автосоздание папок
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.model = None
        self.is_trained = False
        self.load_model()

    def normalize_hand(self, landmarks):
        """
        МЯСО: Делает распознавание независимым от положения руки.
        Вызывается в VideoWorker перед сохранением или предсказанием.
        """
        if not landmarks:
            return [0.0] * 63
        
        # 1. Центрирование по запястью
        wrist = landmarks.landmark[0]
        pts = []
        for lm in landmarks.landmark:
            pts.append([lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z])
        
        # 2. Нормализация масштаба
        max_dist = max([np.linalg.norm(p) for p in pts]) if pts else 1.0
        if max_dist < 0.0001: max_dist = 1.0
        
        flat = []
        for p in pts:
            flat.extend([p[0]/max_dist, p[1]/max_dist, p[2]/max_dist])
        return flat

    def load_model(self):
        """Загрузка обученной модели"""
        if os.path.exists(self.model_file):
            try:
                self.model = joblib.load(self.model_file)
                self.is_trained = True
                print("[ENGINE] Model loaded.")
                return True
            except:
                print("[ENGINE] Model corruption detected.")
        return False

    def save_dataset(self, new_X, new_y):
        """Сохранение новых жестов в .npz с бэкапом"""
        if len(new_X) == 0: return 0

        # БЭКАП перед записью
        if os.path.exists(self.data_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(self.data_file, os.path.join(self.backup_dir, f"backup_{timestamp}.npz"))
            
            # Загрузка старых и объединение
            loaded = np.load(self.data_file, allow_pickle=True)
            X = np.vstack((loaded['X'], np.array(new_X)))
            y = np.concatenate((loaded['y'], np.array(new_y)))
        else:
            X = np.array(new_X)
            y = np.array(new_y)

        np.savez(self.data_file, X=X, y=y)
        return len(new_X)

    def remove_label(self, label_to_remove):
        """
        ТОЧЕЧНОЕ УДАЛЕНИЕ: вырезает жест из бинарного файла .npz
        """
        if not os.path.exists(self.data_file):
            return False, "Database file not found."

        try:
            # 1. Загружаем текущие данные
            data = np.load(self.data_file, allow_pickle=True)
            X, y = data['X'], data['y']

            # 2. Создаем маску для фильтрации
            mask = (y != label_to_remove)
            removed_count = len(y) - np.sum(mask)

            if removed_count == 0:
                return False, f"Gesture '{label_to_remove}' not found."

            # 3. Фильтруем
            new_X = X[mask]
            new_y = y[mask]

            # 4. Сохраняем обратно (если что-то осталось)
            if len(new_y) > 0:
                np.savez(self.data_file, X=new_X, y=new_y)
            else:
                os.remove(self.data_file) # Если удалили последний жест

            # 5. Переобучаем модель
            success, msg = self.train()
            return True, f"Successfully removed {removed_count} samples. {msg}"

        except Exception as e:
            return False, f"Error during removal: {str(e)}"

    def train(self):
        """Обучение RandomForest на всех ядрах CPU"""
        if not os.path.exists(self.data_file):
            return False, "Dataset empty."

        try:
            data = np.load(self.data_file, allow_pickle=True)
            X, y = data['X'], data['y']

            classes = np.unique(y)
            if len(classes) < 2:
                return False, "Need at least 2 different gestures to train."

            # Настройки для "Мяса": n_jobs=-1 использует весь процессор
            clf = RandomForestClassifier(n_estimators=100, max_depth=20, n_jobs=-1)
            clf.fit(X, y)
            
            joblib.dump(clf, self.model_file)
            self.model = clf
            self.is_trained = True
            
            return True, f"Trained on {len(X)} samples ({len(classes)} classes)."
        except Exception as e:
            return False, f"Training error: {str(e)}"

    def predict(self, features):
        """Предсказание (126,) -> (Label, Conf)"""
        if not self.is_trained or self.model is None:
            return "...", 0.0
        
        try:
            feat_arr = np.array(features).reshape(1, -1)
            probs = self.model.predict_proba(feat_arr)[0]
            idx = np.argmax(probs)
            return self.model.classes_[idx], probs[idx]
        except:
            return "...", 0.0