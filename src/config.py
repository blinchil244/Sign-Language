# src/config.py
import cv2

# --- НАСТРОЙКИ СИСТЕМЫ ---
CAMERA_ID = 0  # 0 для вебки, 1 для внешней
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS_LIMIT = 60

# --- ПАЛИТРА ИНТЕРФЕЙСА (CYBERPUNK) ---
COLORS = {
    "primary": "#00E5FF",    # Неоновый голубой
    "secondary": "#FF1744",  # Неоновый красный
    "bg": "#121212",         # Черный фон
    "surface": "#1E1E1E",    # Серые панели
    "text_main": "#E0E0E0",  # Белый текст
    "success": "#00C853",    # Зеленый
    "warning": "#FFD600"     # Желтый
}

# --- ЛОКАЛИЗАЦИЯ (RU / KZ / EN) ---
TRANSLATIONS = {
    "RU": {
        "window_title": "NEURAL SIGN LANGUAGE ULTIMATE",
        "tab_main": "📹 ГЛАВНЫЙ ТЕРМИНАЛ",
        "tab_settings": "⚙️ НАСТРОЙКИ СИСТЕМЫ",
        "grp_camera": "ВИДЕО ПОТОК [LIVE]",
        "grp_control": "ПАНЕЛЬ УПРАВЛЕНИЯ",
        "lbl_input": "Название жеста (ID):",
        "btn_record_hold": "🔴 ЗАЖАТЬ ДЛЯ ЗАПИСИ",
        "btn_record_release": "⏹ ОТПУСТИТЬ",
        "btn_save": "💾 СОХРАНИТЬ БАЗУ",
        "btn_train": "🧠 ОБУЧИТЬ НЕЙРОСЕТЬ",
        "status_ready": "СИСТЕМА ГОТОВА",
        "status_rec": "ИДЕТ ЗАПИСЬ КАДРОВ...",
        "status_train": "ОБУЧЕНИЕ МОДЕЛИ...",
        "msg_saved": "Датасет успешно сохранен!",
        "msg_train_ok": "Модель обучена! Точность: Высокая",
        "msg_train_fail": "Ошибка обучения (мало данных)",
        "lbl_mirror": "Зеркальный режим камеры",
        "lbl_lang": "Язык интерфейса / Тіл:",
        "log_start": ">> Система инициализирована...",
        "mode_col": "РЕЖИМ: СБОР ДАННЫХ",
        "mode_pred": "РЕЖИМ: РАСПОЗНАВАНИЕ"
    },
    "KZ": {
        "window_title": "NEURAL SIGN LANGUAGE ULTIMATE (KZ)",
        "tab_main": "📹 БАСТЫ ТЕРМИНАЛ",
        "tab_settings": "⚙️ ЖҮЙЕ БАПТАУЛАРЫ",
        "grp_camera": "БЕЙНЕ АҒЫНЫ [LIVE]",
        "grp_control": "БАСҚАРУ ПАНЕЛІ",
        "lbl_input": "Ишарат атауы (ID):",
        "btn_record_hold": "🔴 ЖАЗУ ҮШІН БАСЫП ТҰРЫҢЫЗ",
        "btn_record_release": "⏹ ТОҚТАТУ",
        "btn_save": "💾 БАЗАНЫ САҚТАУ",
        "btn_train": "🧠 НЕЙРОЖЕЛІНІ ОҚЫТУ",
        "status_ready": "ЖҮЙЕ ДАЙЫН",
        "status_rec": "КАДРЛАР ЖАЗЫЛУДА...",
        "status_train": "МОДЕЛЬ ОҚЫТЫЛУДА...",
        "msg_saved": "Дерекқор сәтті сақталды!",
        "msg_train_ok": "Модель оқытылды! Дәлдік: Жоғары",
        "msg_train_fail": "Оқыту қатесі (деректер аз)",
        "lbl_mirror": "Камераны айнадай көрсету",
        "lbl_lang": "Тілді таңдау:",
        "log_start": ">> Жүйе іске қосылды...",
        "mode_col": "РЕЖИМ: ДЕРЕК ЖИНАУ",
        "mode_pred": "РЕЖИМ: ТАНУ"
    },
    "EN": {
        "window_title": "NEURAL SIGN LANGUAGE ULTIMATE",
        "tab_main": "📹 MAIN TERMINAL",
        "tab_settings": "⚙️ SYSTEM SETTINGS",
        "grp_camera": "VIDEO STREAM [LIVE]",
        "grp_control": "CONTROL PANEL",
        "lbl_input": "Gesture Name (ID):",
        "btn_record_hold": "🔴 HOLD TO RECORD",
        "btn_record_release": "⏹ RELEASE TO STOP",
        "btn_save": "💾 SAVE DATABASE",
        "btn_train": "🧠 TRAIN NEURAL NET",
        "status_ready": "SYSTEM READY",
        "status_rec": "RECORDING FRAMES...",
        "status_train": "TRAINING MODEL...",
        "msg_saved": "Database saved successfully!",
        "msg_train_ok": "Model trained! Accuracy: High",
        "msg_train_fail": "Training error (insufficient data)",
        "lbl_mirror": "Mirror Camera Mode",
        "lbl_lang": "Interface Language:",
        "log_start": ">> System initialized...",
        "mode_col": "MODE: DATA COLLECTION",
        "mode_pred": "MODE: PREDICTION"
    }
}