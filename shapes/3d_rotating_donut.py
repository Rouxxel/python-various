#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
3D rotating Donut by Andy Sloane
The implementation of Andy Sloane's code for a rotating 3D donut
"""

import tkinter as tk
import math

class DonutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rotating ASCII Donut")
        self.text = tk.Text(root, width=80, height=24, font=("Courier", 10), bg="black", fg="lime", bd=0)
        self.text.pack()
        self.A = 0
        self.B = 0
        self.update_frame()

    def update_frame(self):
        output, self.A, self.B = self.generate_donut_frame(self.A, self.B)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, output)
        self.root.after(30, self.update_frame)  # 30ms delay ≈ 33 FPS

    def generate_donut_frame(self, A, B):
        z = [0] * 1760
        b = [' '] * 1760
        for j in range(0, 628, 7):
            for i in range(0, 628, 2):
                c = math.sin(i / 100)
                d = math.cos(j / 100)
                e = math.sin(A)
                f = math.sin(j / 100)
                g = math.cos(A)
                h = d + 2
                D = 1 / (c * h * e + f * g + 5)
                l = math.cos(i / 100)
                m = math.cos(B)
                n = math.sin(B)
                t = c * h * g - f * e
                x = int(40 + 30 * D * (l * h * m - t * n))
                y = int(12 + 15 * D * (l * h * n + t * m))
                o = x + 80 * y
                N = int(8 * ((f * e - c * d * g) * m - c * d * e - f * g - l * d * n))
                if 0 <= y < 22 and 0 <= x < 80 and D > z[o]:
                    z[o] = D
                    b[o] = ".,-~:;=!*#$@"[max(0, N)]
        frame = ''.join(b[i] if i % 80 else '\n' for i in range(1760))
        return frame, A + 0.04, B + 0.08

if __name__ == "__main__":
    root = tk.Tk()
    app = DonutApp(root)
    root.mainloop()
