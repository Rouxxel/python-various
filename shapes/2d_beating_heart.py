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
        self.root.title("Beating ASCII Heart ❤️")
        self.canvas = tk.Canvas(root, width=500, height=500, bg='black')
        self.canvas.pack()
        self.frame = 0
        self.update_heart()

    def update_heart(self):
        self.canvas.delete("all")
        scale = 10 + 2 * math.sin(self.frame / 5)  # creates beating effect

        for t in range(0, 628, 1):  # 0 to 2π
            t = t / 100
            x = 16 * math.sin(t)**3
            y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)

            screen_x = 250 + int(x * scale)
            screen_y = 250 - int(y * scale)

            self.canvas.create_text(screen_x, screen_y, text='*', fill='red', font=('Courier', 8))

        self.frame += 1
        self.root.after(50, self.update_heart)

if __name__ == "__main__":
    root = tk.Tk()
    app = HeartApp(root)
    root.mainloop()
