#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import math

#This does not work how i want it
class BeatingHeart3DApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Beating Heart ❤️")
        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.frame = 0
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        self.pixel_size = 1
        self.root.bind('<Configure>', self.on_resize)
        self.update_heart()

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height

    def heart_3d(self, u, v):
        """Parametric 3D heart surface (polar-based)"""
        r = 1 - math.sin(u)
        x = r * math.cos(u) * math.sin(v)
        y = r * math.sin(u) * math.sin(v)
        z = r * math.cos(v)
        return x, y, z

    def rotate(self, x, y, z, ax, ay, az):
        """Rotate point (x, y, z) by angles ax, ay, az (in radians)"""
        # X-axis
        y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
        # Y-axis
        x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
        # Z-axis
        x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
        return x, y, z

    def project(self, x, y, z, scale=20):
        """Simple orthographic projection with scaling"""
        return int(self.width / 2 + x * scale), int(self.height / 2 - y * scale)

    def update_heart(self):
        self.canvas.delete("all")
        angle = self.frame / 30
        beat_scale = 1 + 0.2 * math.sin(self.frame / 5)

        for i in range(0, 90, 2):
            for j in range(0, 360, 4):
                u = math.radians(i)
                v = math.radians(j)

                x, y, z = self.heart_3d(u, v)
                x *= beat_scale
                y *= beat_scale
                z *= beat_scale

                x, y, z = self.rotate(x, y, z, angle, angle, 0)

                screen_x, screen_y = self.project(x, y, z)

                brightness = int(128 + 127 * z)  # based on z-depth
                brightness = max(0, min(255, brightness))
                color = f"#{brightness:02x}0000"

                self.canvas.create_text(screen_x, screen_y, text='█', fill=color, font=('Courier', self.pixel_size))

        self.frame += 1
        self.root.after(50, self.update_heart)

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", False)
    app = BeatingHeart3DApp(root)
    root.mainloop()
