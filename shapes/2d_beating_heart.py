#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
2D beating Donut
Implementation of a code that creates a beating heart in 2D
"""

import tkinter as tk
import math

class HeartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Beating, scalable Heart ❤️")

        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.frame = 0
        
        self.pixel_size = 15 #Level of detail, the bigger the faster
        
        #Color and brightness
        self.color_base_red = 255      #max red component
        self.color_min_red = 0         #min red component
        self.color_brightness_factor = 1.0 / 1.5  #factor to scale y for brightness calculation
        
        self.root.bind('<Configure>', self.on_resize)
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        self.update_heart()

    def on_resize(self, event):
        """Update canvas size on window resize."""
        self.width = event.width
        self.height = event.height

    def heart_equation(self, x, y):
        return (x**2 + y**2 - 1)**3 - x**2 * y**3 <= 0

    def get_heart_color(self, y):
        brightness = int((1 - y * self.color_brightness_factor) * self.color_base_red)
        brightness = max(self.color_min_red, min(self.color_base_red, brightness))
        return f"#{brightness:02x}0000"

    def update_heart(self):
        self.canvas.delete("all") #Delete each frame to create animation effect
        scale = min(self.width, self.height) / 30 + 2 * math.sin(self.frame / 5)

        for i in range(-30, 31):
            for j in range(-30, 31):
                x = i / 15.0
                y = j / 15.0

                if self.heart_equation(x, y):
                    color = self.get_heart_color(y)

                    screen_x = self.width // 2 + int(i * scale / 3)
                    screen_y = self.height // 2 - int(j * scale / 3)

                    self.canvas.create_text(screen_x, 
                                            screen_y, 
                                            text='█', 
                                            fill=color, 
                                            font=('Courier',self.pixel_size))

        self.frame = self.frame + 1
        self.root.after(50, self.update_heart)

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", False)  # or use root.state("zoomed") on Windows
    app = HeartApp(root)
    root.mainloop()
