#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import math

class InfinitySymbol3DApp:
    def __init__(self, root, resolution=200, pixel_size=4, rotation_speed=0.03, scale_factor=10):
        self.root = root
        self.root.title("3D Infinity Symbol ∞")

        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.frame = 0
        self.resolution = resolution
        self.pixel_size = pixel_size
        self.rotation_speed = rotation_speed
        self.scale_factor = scale_factor

        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        self.scale = min(self.width, self.height) / self.scale_factor
        self.root.bind('<Configure>', self.on_resize)

        self.update_animation()

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.scale = min(self.width, self.height) / self.scale_factor

    def infinity_curve_3d(self, t):
        """Parametric 3D infinity curve (lemniscate-like)"""
        a = 1.0
        x = a * math.sin(t)
        y = a * math.sin(t) * math.cos(t)
        z = 0.5 * a * math.cos(2 * t)
        return x, y, z

    def rotate(self, x, y, z, ax, ay, az):
        """Rotate point (x, y, z) around X, Y, Z axes by angles ax, ay, az (in radians)"""
        # Rotate around X
        y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
        # Rotate around Y
        x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
        # Rotate around Z
        x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
        return x, y, z

    def project(self, x, y, z):
        """Project 3D to 2D"""
        return int(self.width / 2 + x * self.scale), int(self.height / 2 - y * self.scale)

    def update_animation(self):
        self.canvas.delete("all")
        angle = self.frame * self.rotation_speed

        for i in range(self.resolution):
            t = (2 * math.pi * i) / self.resolution
            x, y, z = self.infinity_curve_3d(t)

            x, y, z = self.rotate(x, y, z, angle, angle / 2, angle / 3)
            screen_x, screen_y = self.project(x, y, z)

            # Depth-based color (z controls brightness)
            brightness = int(128 + 127 * z)
            brightness = max(0, min(255, brightness))
            color = f"#{brightness:02x}{brightness:02x}ff"

            size = self.pixel_size
            self.canvas.create_rectangle(
                screen_x, screen_y, screen_x + size, screen_y + size,
                outline=color, fill=color
            )

        self.frame = self.frame + 1
        self.root.after(30, self.update_animation)

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", False)
    app = InfinitySymbol3DApp(root,
                                resolution=300,
                                pixel_size=3,
                                rotation_speed=0.04,
                                scale_factor=8)
    root.mainloop()
