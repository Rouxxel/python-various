#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import math

class PsycodelicRoseCurveApp:
    def __init__(self, root, width=600, height=600):
        self.root = root
        self.root.title("2D Rose Curve (Rhodonea)")

        self.width = width
        self.height = height
        self.canvas = tk.Canvas(root, width=width, height=height, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.center_x = width // 2
        self.center_y = height // 2

        self.max_radius = min(self.center_x, self.center_y) * 0.9

        self.frame = 0
        self.points_count = 1000  # points per curve

        # Animation parameters
        self.k_min = 2
        self.k_max = 8
        self.k = self.k_min
        self.k_speed = 0.02  # how fast k morphs
        self.growing = True

        self.update_animation()

    def rose_point(self, theta, a, k):
        """Calculate (x, y) for rose curve at angle theta with amplitude a and petal count k"""
        r = a * math.sin(k * theta)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        return x, y

    def update_animation(self):
        self.canvas.delete("all")

        # Animate amplitude (petal "growing") from 0 to max_radius and back
        amplitude = self.max_radius * (0.5 + 0.5 * math.sin(self.frame * 0.05))

        # Animate k smoothly morphing between k_min and k_max
        # We'll make k oscillate smoothly for petal count morph effect
        k_val = self.k_min + (self.k_max - self.k_min) * (0.5 + 0.5 * math.sin(self.frame * self.k_speed))
        
        points = []
        for i in range(self.points_count + 1):
            theta = 2 * math.pi * i / self.points_count
            x, y = self.rose_point(theta, amplitude, k_val)
            # Convert to canvas coords (flip y to have +y downwards)
            px = self.center_x + x
            py = self.center_y - y
            points.append((px, py))

        # Draw curve as connected lines
        for i in range(len(points) - 1):
            # Color changes along petals for effect
            color_val = int(128 + 127 * math.sin(i * 0.1 + self.frame * 0.1))
            color_val = max(0, min(255, color_val))
            color = f'#{color_val:02x}{(255 - color_val):02x}{255:02x}'  # gradient cyan-magenta

            self.canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=color, width=2)

        self.frame = self.frame + 1
        self.root.after(30, self.update_animation)


if __name__ == "__main__":
    root = tk.Tk()
    app = PsycodelicRoseCurveApp(root)
    root.mainloop()
