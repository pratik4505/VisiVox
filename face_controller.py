# face_controller.py (updated)
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from threading import Thread
import sys
import os

pyautogui.FAILSAFE = False

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    os.environ['MEDIAPIPE_MODEL_PATH'] = os.path.join(
        base_path, 
        'mediapipe/modules'
    )

class FaceController(Thread):
    def __init__(self, params):
        super().__init__()
        self.needs_recalibration = False
        self.params = params
        self.paused = False
        self.running = True
        self._setup_mediapipe()
        self._initialize_state()
        
    def _setup_mediapipe(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8)
        
    def _initialize_state(self):
        self.prev_smooth_x = 0.5
        self.prev_smooth_y = 0.5
        self.blink_counter = 0
        self.ear_threshold = None
        self.normal_ear = 0
        self.normal_mouth = 0
        self.calibration_eyebrow_left = 0
        self.calibration_eyebrow_right = 0
        self.waiting_for_double = False
        self.first_blink_time = 0
        self.last_right_click_time = 0
        self.scrolling = False
        self.scroll_direction = None
        self.initial_smooth_x = None
        self.initial_smooth_y = None
        self.last_scroll_time = 0
        self.mouth_open_threshold = 0
        self.screen_w, self.screen_h = pyautogui.size()
        
    def run(self):
        cap = cv2.VideoCapture(0)
        self._calibrate(cap)  # Use same camera feed
        
        try:
            while self.running:
                # Check for recalibration first
                if self.needs_recalibration:
                    self._calibrate(cap)
                    self.needs_recalibration = False
                
                if not self.paused:
                    self._process_frame(cap)
                
                time.sleep(0.01)
        finally:
            cap.release()
            
    def trigger_recalibration(self):
        """External method to trigger recalibration"""
        self.needs_recalibration = True
            
    def _calibrate(self, cap):
        """Updated calibration using existing camera feed"""
        print("Recalibrating...")
        calibration_counter = 0
        self._initialize_state()
        
        while calibration_counter < self.params['CALIBRATION_FRAMES'] and self.running:
            ret, frame = cap.read()
            if ret:
                results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if results.multi_face_landmarks:
                    self._collect_calibration_data(results.multi_face_landmarks[0].landmark)
                    calibration_counter += 1
        
        self._finalize_calibration()
        print("Recalibration complete")
        
            
    def stop(self):
        self.running = False
        self.join()
        
    def toggle_pause(self):
        self.paused = not self.paused
        
    def update_param(self, key, value):
        self.params[key] = value