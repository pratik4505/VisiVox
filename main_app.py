import tkinter as tk
from tkinter import ttk
from threading import Thread
from mouse_gui import MouseTab


import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mouse Control Center")
        self.geometry("800x600")

        
        self.create_widgets()

    def create_widgets(self):
        # Main window contains only mouse controls
        self.notebook = ttk.Notebook(self)
        
        # Add mouse tab
        self.mouse_tab = MouseTab(self.notebook, self.voice_assistant)
        self.notebook.add(self.mouse_tab, text=" Mouse Control ")
        self.notebook.pack(expand=1, fill="both")

    def on_closing(self):

        self.mouse_tab.stop()
        self.destroy()

if __name__ == "__main__":

    app = MainApplication()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()