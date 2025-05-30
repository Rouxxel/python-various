#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import math

class MobiusStrip3DApp:
    def __init__(self, root, width=800, height=600, pixel_size=3, res_u=100, res_v=30):
        self.root = root
        self.root.title("3D Möbius Strip")

        self.width = width
        self.height = height
        self.canvas = tk.Canvas(root, bg='black', width=width, height=height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.pixel_size = pixel_size
        self.res_u = res_u  # resolution along u
        self.res_v = res_v  # resolution along v
        self.width_factor = 0.2  # smaller = thinner strip

        self.frame = 0
        self.scale_base = min(width, height) / 3
        self.root.bind('<Configure>', self.on_resize)

        self.update_animation()

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.scale_base = min(self.width, self.height) / 3

    def mobius_point(self, u, v):
        wf = self.width_factor
        x = (1 + v * wf * math.cos(u / 2)) * math.cos(u)
        y = (1 + v * wf * math.cos(u / 2)) * math.sin(u)
        z = v * wf * math.sin(u / 2)
        return x, y, z

    def rotate(self, x, y, z, ax, ay, az):
        """Rotate point (x, y, z) by angles ax, ay, az"""
        # Rotate X
        y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
        # Rotate Y
        x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
        # Rotate Z
        x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
        return x, y, z

    def project(self, x, y, z):
        """Simple orthographic projection"""
        px = self.width / 2 + x * self.scale
        py = self.height / 2 - y * self.scale
        return int(px), int(py)

    def update_animation(self):
        self.canvas.delete("all")

        # Slowly rotate
        angle_x = self.frame * 0.015
        angle_y = self.frame * 0.01
        angle_z = self.frame * 0.008

        self.scale = self.scale_base

        points = []
        for i in range(self.res_u + 1):
            u = 2 * math.pi * i / self.res_u
            for j in range(self.res_v + 1):
                v = -1 + 2 * j / self.res_v

                x, y, z = self.mobius_point(u, v)
                x, y, z = self.rotate(x, y, z, angle_x, angle_y, angle_z)

                px, py = self.project(x, y, z)

                # brightness depends on z for some shading
                brightness = int(100 + 155 * (z + 0.5))  # shift z for better range
                brightness = max(0, min(255, brightness))
                color = f'#{brightness:02x}{brightness:02x}{brightness:02x}'  # grayscale shading

                points.append((px, py, color))

        # Draw points as small circles
        size = self.pixel_size
        for px, py, color in points:
            self.canvas.create_oval(px, py, px + size, py + size, fill=color, outline='')

        self.frame += 1
        self.root.after(30, self.update_animation)

if __name__ == "__main__":
    root = tk.Tk()
    app = MobiusStrip3DApp(root)
    root.mainloop()
