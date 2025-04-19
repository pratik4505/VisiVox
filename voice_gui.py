import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread
import os
import time
from voice_assistant import VoiceAssistant  # New module for VoiceAssistant class
from css import Style  # Styling configurations
from config import Config  # Main configuration

class VoiceTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Remove this line: self.style = Style()
        self.assistant = None
        self.loading_active = False
        self.loading_angle = 0
        self.create_widgets()
        self.start_assistant()
        
    def create_widgets(self):
        # Status Frame
        status_frame = ttk.Frame(self)
        status_frame.pack(pady=10, fill=tk.X)
        
        # Header
        header = ttk.Label(self, text="Voice Control Assistant", style='Header.TLabel')
        header.pack(pady=(10, 20))
        
        # Status Indicator
        self.status_indicator = ttk.Label(
            status_frame, 
            text="Initializing...",
            foreground="#3498db",
            font=('Helvetica', 10, 'bold')
        )
        self.status_indicator.pack(side=tk.LEFT, padx=10)
        
        # Loading Canvas
        self.canvas = tk.Canvas(self, width=40, height=40, highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, anchor='ne', padx=20)
        self.loading_arc = self.canvas.create_arc(
            10, 10, 30, 30,
            start=0,
            extent=0,
            style=tk.ARC,
            outline="#e74c3c",
            width=3
        )
        
        # Log Display
        log_frame = ttk.Frame(self)
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            state='disabled',
            bg='#ecf0f1',
            font=('Consolas', 9),
            padx=10,
            pady=10
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
    def start_assistant(self):
        try:
            self.log("Starting voice assistant...")
            self.update_status("waiting")
            self.assistant = VoiceAssistant(gui=self)
            assistant_thread = Thread(target=self.assistant.run)
            assistant_thread.daemon = True
            assistant_thread.start()
        except Exception as e:
            self.log(f"Failed to start assistant: {e}")
            self.update_status("error")
        
    def update_status(self, status):
        status_config = {
            "waiting": ("Waiting for wake word...", "#f1c40f"),
            "active": ("Active - Listening", "#2ecc71"),
            "error": ("Error Occurred", "#e74c3c")
        }
        text, color = status_config.get(status, ("Unknown Status", "#95a5a6"))
        self.status_indicator.config(text=text, foreground=color)
        
    def log(self, message):
        def update_log():
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state='disabled')
        
        # Use Tkinter's thread-safe after() method
        self.after(0, update_log)
        
    def start_loading(self):
        self.loading_active = True
        self.animate_loading()

    def stop_loading(self):
        self.loading_active = False
        self.canvas.itemconfig(self.loading_arc, extent=0)

    def animate_loading(self):
        if self.loading_active:
            self.loading_angle = (self.loading_angle + 30) % 360
            self.canvas.itemconfig(self.loading_arc, start=self.loading_angle, extent=270)
            self.after(100, self.animate_loading)
            
    def stop(self):
        if self.assistant:
            self.assistant.is_active = False