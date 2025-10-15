#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Responsive, Shaded, Animated Strawberry in Fullscreen
"""

import tkinter as tk
import math

class StrawberryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Beating Strawberry 🍓")

        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.frame = 0
        
        self.root.bind("<Configure>", self.on_resize)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        
        # Initialize dimensions
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        #Color control
        self.body_base_color = (255, 0, 0)  #red
        self.body_min_brightness = 0.4  #40% minimum brightness
        self.body_brightness_scale = 1.0  #scaling factor for brightness
        
        #Seeds parameters
        self.seed_spacing_x = 0.3  #spacing between seeds in x (normalized units)
        self.seed_spacing_y = 0.3 #spacing between seeds in y
        self.seed_base_color = (255, 255, 0)  #yellow
        self.seed_min_brightness = 0.6  #60%
        self.seed_brightness_amplitude = 0.4  #how much it pulsates
        
        #Leaves parameters
        self.leaf_count = 15
        self.leaf_length_ratio = 0.5  #relative to height
        self.leaf_width_ratio = 0.3   #relative to width
        self.leaf_fill_color = '#00aa00'       #any color string
        self.leaf_outline_color = '#006600'
        #to be updated later
        self.leaf_length = None
        self.leaf_width = None
        self.top_y = None
        
        self.update_strawberry()

#######################################################################################
    def on_resize(self, event):
        """Update canvas size on window resize."""
        self.width = event.width
        self.height = event.height
        
    def apply_brightness(self, rgb, brightness_factor):
        r, g, b = rgb
        r = int(max(0, min(255, r * brightness_factor)))
        g = int(max(0, min(255, g * brightness_factor)))
        b = int(max(0, min(255, b * brightness_factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def is_in_strawberry(self, x, y):
        #x, y normalized coordinates centered at (0,0)        
        #Define a flat top by restricting y > -0.5
        if y > 0.8:  # cut off upper y to flatten top
            return False

        #Check ellipse shape (body)
        #width wider than height near top
        ellipse_eq = (x / 1.0)**2 + (y / 1.3)**2

        #Make ellipse cut off below y = -1.0 for pointy bottom
        if y < -1.0:
            return False

        #Below 0, taper to a point by shrinking width
        if y < 0:
            taper = 1 + y 
            if abs(x) > taper:
                return False

        return ellipse_eq <= 1

    def draw_strawberry_parametric(self, scale):
        x_center = self.width // 2
        y_center = self.height // 2
        width = scale * self.width * 0.13
        height = scale * self.height * 0.2

        # Dynamically adjust pixel size based on window size (bigger pixels for larger windows)
        self.pixel_size = max(3, min(self.width, self.height) // 40)
        
        # Dynamically adjust seed radius based on pixel size
        self.seed_radius = max(1, self.pixel_size // 3)

        # Update leaf sizes now that width/height/scale are known
        self.leaf_length = height * self.leaf_length_ratio
        self.leaf_width = width * self.leaf_width_ratio
        self.top_y = y_center - height * 0.8

        steps_x = 60
        steps_y = 80

        for i in range(-steps_x, steps_x + 1, self.pixel_size):
            for j in range(-steps_y, steps_y + 1, self.pixel_size):
                x = i / steps_x
                y = -(j / steps_y ) 
                
                if self.is_in_strawberry(x, y):
                    brightness = (1 - y) * self.body_brightness_scale
                    brightness = max(self.body_min_brightness, min(1.0, brightness))
                    color = self.apply_brightness(self.body_base_color, brightness)
                    px = int(x_center + x * width)
                    py = int(y_center - y * height)
                    self.canvas.create_rectangle(
                        px, py, px + self.pixel_size, py + self.pixel_size,
                        outline=color, fill=color
                    )
        
        #Loop over seed positions in normalized coordinates
        seed_spacing_x_scaled = self.seed_spacing_x * width
        seed_spacing_y_scaled = self.seed_spacing_y * height
        for sx in range(-3, 5):
            for sy in range(-3, 5):
                if self.is_in_strawberry(sx * self.seed_spacing_x, sy * self.seed_spacing_y):
                    pulse = 0.5 + 0.5 * math.sin(self.frame / 10 + sx * 10 + sy * 10)
                    brightness = self.seed_min_brightness + self.seed_brightness_amplitude * pulse
                    brightness = min(1.0, max(0.0, brightness))
                    
                    color = self.apply_brightness(self.seed_base_color, brightness)

                    px = int(x_center + sx * seed_spacing_x_scaled)
                    py = int(y_center - sy * seed_spacing_y_scaled)

                    self.canvas.create_oval(
                        px - self.seed_radius, py - self.seed_radius,
                        px + self.seed_radius, py + self.seed_radius,
                        fill=color, outline=""
                    )
        
        #Render leafs on top of body and seeds
        for i in range(self.leaf_count):
            angle = (i - self.leaf_count // 2) * 15
            base_x = x_center + math.sin(math.radians(angle)) * self.leaf_width
            base_y = self.top_y + math.cos(math.radians(angle)) * self.leaf_width / 2

            tip_x = base_x + math.sin(math.radians(angle)) * self.leaf_length
            tip_y = base_y - math.cos(math.radians(angle)) * self.leaf_length

            left_x = base_x + math.cos(math.radians(angle)) * self.leaf_width / 2
            left_y = base_y + math.sin(math.radians(angle)) * self.leaf_width / 2

            right_x = base_x - math.cos(math.radians(angle)) * self.leaf_width / 2
            right_y = base_y - math.sin(math.radians(angle)) * self.leaf_width / 2

            self.canvas.create_polygon(
                tip_x, tip_y,
                left_x, left_y,
                right_x, right_y,
                fill=self.leaf_fill_color,
                outline=self.leaf_outline_color
            )

    def update_strawberry(self):
        self.canvas.delete("all")
        scale = 1 + 0.1 * math.sin(self.frame / 10)
        self.draw_strawberry_parametric(scale)
        self.frame = self.frame + 1
        self.root.after(60, self.update_strawberry)

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", False)  # Fullscreen
    app = StrawberryApp(root)
    root.mainloop()
