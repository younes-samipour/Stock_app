import tkinter as tk
from tkinter import ttk
from datetime import datetime
from time import time

class DigitalClock(ttk.Frame):
    def __init__(self, parent, is_stopwatch=False):
        super().__init__(parent)
        self.is_stopwatch = is_stopwatch
        self.running = False  # تعریف متغیر running
        
        self.time_var = tk.StringVar()
        self.time_var.set("00:00:00" if is_stopwatch else datetime.now().strftime('%H:%M:%S'))
        
        self.label = ttk.Label(self, textvariable=self.time_var, font=('Arial', 12))
        self.label.pack()
        
        if not is_stopwatch:
            self.update_clock()
        
        # متغیرهای مربوط به کرنومتر
        self.start_time = 0
        self.elapsed = 0
    
    def update_clock(self):
        if not self.is_stopwatch and not self.running:
            self.time_var.set(datetime.now().strftime('%H:%M:%S'))
            self.after(1000, self.update_clock)
    
    def start(self):
        if self.is_stopwatch and not self.running:
            self.running = True
            self.start_time = time()
            self.update_stopwatch()
    
    def stop(self):
        if self.is_stopwatch:
            self.running = False
            self.elapsed += time() - self.start_time
    
    def reset(self):
        if self.is_stopwatch:
            self.running = False
            self.elapsed = 0
            self.time_var.set("00:00:00")
    
    def update_stopwatch(self):
        if self.running:
            elapsed = self.elapsed + (time() - self.start_time)
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.time_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.after(1000, self.update_stopwatch)