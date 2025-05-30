#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import math

class BeatingRedGlobuleStream3DApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Beating RedGlobuleStream ❤️")
        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.frame = 0
        self.pixel_size = 5  # Smaller = more points, bigger = faster
        self.resolution_u = 30
        self.resolution_v = 60

        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        self.scale = min(self.width, self.height) / 10  # Dynamic scaling
        self.root.bind('<Configure>', self.on_resize)

        self.update_RedGlobuleStream()

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.scale = min(self.width, self.height) / 10

    def RedGlobuleStream_3d(self, u, v):
        """Parametric 3D RedGlobuleStream surface"""
        r = 1 - math.sin(u)
        x = r * math.cos(u) * math.sin(v)
        y = r * math.sin(u) * math.sin(v)
        z = r * math.cos(v)
        return x, y, z

    def rotate(self, x, y, z, ax, ay, az):
        """Rotate point (x, y, z) by angles ax, ay, az (in radians)"""
        y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
        x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
        x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
        return x, y, z

    def project(self, x, y, z):
        """Project 3D to 2D with dynamic scale"""
        return int(self.width / 2 + x * self.scale), int(self.height / 2 - y * self.scale)

    def update_RedGlobuleStream(self):
        self.canvas.delete("all")
        angle = self.frame / 30
        beat_scale = 1 + 0.2 * math.sin(self.frame / 5)

        for i in range(0, 90, int(90 / self.resolution_u)):
            for j in range(0, 360, int(360 / self.resolution_v)):
                u = math.radians(i)
                v = math.radians(j)

                x, y, z = self.RedGlobuleStream_3d(u, v)
                x *= beat_scale
                y *= beat_scale
                z *= beat_scale

                x, y, z = self.rotate(x, y, z, angle, angle, 0)
                screen_x, screen_y = self.project(x, y, z)

                brightness = int(128 + 127 * z)
                brightness = max(0, min(255, brightness))
                color = f"#{brightness:02x}0000"

                size = self.pixel_size
                self.canvas.create_rectangle(
                    screen_x, screen_y, screen_x + size, screen_y + size,
                    outline=color, fill=color
                )

        self.frame = self.frame + 1
        self.root.after(30, self.update_RedGlobuleStream)

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", False)
    app = BeatingRedGlobuleStream3DApp(root)
    root.mainloop()
