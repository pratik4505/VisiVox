# mouse_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from face_controller import FaceController
import keyboard


import time

DEFAULT_PARAMS = {
    'EMA_ALPHA': 0.15,
    'CURSOR_SENSITIVITY_X': 8,
    'CURSOR_SENSITIVITY_Y': 8,
    'BLINK_THRESHOLD_RATIO': 0.75,
    'CALIBRATION_FRAMES': 30,
    'MOVEMENT_THRESHOLD': 0.02,
    'DOUBLE_CLICK_THRESHOLD': 0.8,
    'EYEBROW_RAISE_THRESHOLD_RATIO': 1.4,
    'RIGHT_CLICK_COOLDOWN': 1.0,
    'MOUTH_OPEN_THRESHOLD_RATIO': 1.5,
    'SCROLL_THRESHOLD': 0.03,
    'SCROLL_STEP': 50,
    'SCROLL_INTERVAL': 0.05
}

class MouseTab(ttk.Frame):
    def __init__(self, master, voice_assistant):  # Add second parameter
        super().__init__(master)
        self.params = DEFAULT_PARAMS.copy()
        self.face_controller = FaceController(self.params)
        self.face_controller.start()
        self.voice_assistant = voice_assistant
        self.entries = {}
        self.create_widgets()
        self.setup_hotkeys()
        
    def create_widgets(self):
        # Header
        header = ttk.Label(self, text="Facial Mouse Control", style='Header.TLabel')
        header.pack(pady=(10, 20), anchor=tk.CENTER)

        # Status Label
        self.status_label = ttk.Label(
            self,
            text="Status: Active",
            foreground="green",
            font=('Helvetica', 10)
        )
        self.status_label.pack(pady=5)

        # Parameters Frame
        params_frame = ttk.Frame(self, style='Card.TFrame')
        params_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        parameters = [
            ('EMA Alpha', 'EMA_ALPHA'),
            ('Cursor Sensitivity X', 'CURSOR_SENSITIVITY_X'),
            ('Cursor Sensitivity Y', 'CURSOR_SENSITIVITY_Y'),
            ('Blink Threshold', 'BLINK_THRESHOLD_RATIO'),
            ('Calibration Frames', 'CALIBRATION_FRAMES'),
            ('Movement Threshold', 'MOVEMENT_THRESHOLD'),
            ('Double Click Threshold', 'DOUBLE_CLICK_THRESHOLD'),
            ('Eyebrow Raise Ratio', 'EYEBROW_RAISE_THRESHOLD_RATIO'),
            ('Right Click Cooldown', 'RIGHT_CLICK_COOLDOWN'),
            ('Mouth Open Ratio', 'MOUTH_OPEN_THRESHOLD_RATIO'),
            ('Scroll Threshold', 'SCROLL_THRESHOLD'),
            ('Scroll Step', 'SCROLL_STEP'),
            ('Scroll Interval', 'SCROLL_INTERVAL')
        ]

