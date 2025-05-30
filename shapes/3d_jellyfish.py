#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import math

class Jellyfish3DApp:
    def __init__(self, root, width=800, height=600, pixel_size=4, resolution_theta=20, resolution_phi=30):
        self.root = root
        self.root.title("3D Jellyfish")

        self.canvas = tk.Canvas(root, bg='black', width=width, height=height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.width = width
        self.height = height
        self.pixel_size = pixel_size
        self.res_theta = resolution_theta  # vertical angle steps
        self.res_phi = resolution_phi      # horizontal angle steps

        self.frame = 0
        self.scale_base = min(width, height) / 4
        self.root.bind('<Configure>', self.on_resize)

        self.update_animation()

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.scale_base = min(self.width, self.height) / 4

    def hemisphere_point(self, theta, phi):
        """
        Parametric hemisphere:
        theta: 0..pi/2 (from top down)
        phi: 0..2pi around
        """
        r = 1
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)  # dome shape, z >= 0
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
        """Simple orthographic projection with scaling"""
        px = self.width / 2 + x * self.scale
        py = self.height / 2 - y * self.scale
        return int(px), int(py)

    def tentacle_point(self, base_x, base_y, t, phase, length=100, segments=30):
        """
        Generate a single tentacle point:
        base_x, base_y = anchor point on body
        t = time/frame for animation
        phase = phase shift of sine wave for this tentacle
        length = tentacle length in pixels
        segments = how many points along tentacle (returns last segment point)
        """
        points = []
        for i in range(segments):
            # Along vertical direction, y decreases downward
            y = base_y + i * (length / segments)

            # Wiggle x by sine wave that travels downward along tentacle
            wiggle = 10 * math.sin(t * 0.2 + phase + i * 0.5)

            points.append((base_x + wiggle, y))
        return points

    def update_animation(self):
        self.canvas.delete("all")

        # Pulse scale from 0.85 to 1.15 smoothly
        pulse = 1 + 0.15 * math.sin(self.frame * 0.1)
        self.scale = self.scale_base * pulse

        # Rotation angle for vertical rotation only (around X axis)
        angle_x = self.frame * 0.03  # adjust speed here
        angle_y = 0
        angle_z = 0

        # Draw hemisphere dome points
        for i in range(self.res_theta + 1):
            theta = (math.pi / 2) * i / self.res_theta  # from 0 to pi/2
            for j in range(self.res_phi):
                phi = (2 * math.pi) * j / self.res_phi

                x, y, z = self.hemisphere_point(theta, phi)

                # Rotate only around X axis (vertical spin)
                x, y, z = self.rotate(x, y, z, angle_x, angle_y, angle_z)

                # Apply pulse scaling (body beats)
                x *= pulse
                y *= pulse
                z *= pulse

                # Project to 2D
                px, py = self.project(x, y, z)

                # Color: blueish with brightness based on z height (dome curvature)
                brightness = int(100 + 155 * (z / 1.0))
                brightness = max(0, min(255, brightness))
                color = f'#00{brightness:02x}{brightness:02x}'  # shades of cyan

                # Draw pixel (oval)
                size = self.pixel_size
                self.canvas.create_oval(px, py, px + size, py + size, fill=color, outline='')

        # Tentacle base positions under the dome (around bottom edge)
        tentacle_count = 8
        base_radius = self.scale * 0.9
        tentacle_length = self.height / 3

        for k in range(tentacle_count):
            # Tentacle bases rotated same as dome rotation around X axis
            # Since rotation is vertical, only y,z change - we must compute the base_x, base_y properly

            # Original base points on circle (in x,y plane)
            angle = 2 * math.pi * k / tentacle_count
            bx = base_radius * math.cos(angle)
            by = base_radius * math.sin(angle)
            bz = 0  # base on hemisphere edge (z=0 plane)

            # Rotate base point around X
            # Using rotation matrix for X axis:
            # y' = y*cos(ax) - z*sin(ax)
            # z' = y*sin(ax) + z*cos(ax)
            ry = by * math.cos(angle_x) - bz * math.sin(angle_x)
            rz = by * math.sin(angle_x) + bz * math.cos(angle_x)

            # Project tentacle base (base_x, base_y) on canvas
            base_x = bx
            base_y = rz + self.height / 2 + self.scale * 0.3  # use rz as vertical offset

            # Tentacle points with wiggle
            points = []
            segments = 30
            for i in range(segments):
                # vertical y spaced downward from base_y
                y = base_y + i * (tentacle_length / segments)
                # wiggle x by sine wave traveling downward
                wiggle_x = 20 * math.sin(self.frame * 0.2 + k + i * 0.4)
                x = base_x + wiggle_x + self.width / 2
                points.append((x, y))

            # Draw tentacle as connected small circles
            for px, py in points:
                brightness = int(150 + 105 * math.sin(self.frame * 0.1 + px * 0.05))
                brightness = max(0, min(255, brightness))
                color = f'#00{brightness:02x}{brightness:02x}'  # cyan shades
                size = self.pixel_size
                self.canvas.create_oval(px, py, px + size, py + size, fill=color, outline='')

        self.frame += 1
        self.root.after(30, self.update_animation)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = Jellyfish3DApp(root)
    root.mainloop()
