#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Geometric figures methods
A simple compilation of methods to print geometric figures
"""

import sys
import logging
import datetime

"""LOGGING SETUP"""
log_file = datetime.datetime.now().strftime("pattern_log_%Y-%m-%d_%H-%M-%S.log")
logger = logging.getLogger("pattern_logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

"""PYRAMID METHODS"""
def full_left_pyramid(line_num):
    if line_num > 0:
        for lines in range(line_num):
            stars = 1 + (2 * lines)
            print("*" * stars)
    else:
        logger.error("Invalid input in full_left_pyramid.")
        return

def full_pyramid(line_num):
    if line_num > 0:
        pyr_base = 1 + ((line_num * 2) - 2)
        for lines in range(line_num):
            stars = 1 + (2 * lines)
            spaces = (pyr_base - stars) // 2
            print(" " * spaces + "*" * stars)
    else:
        logger.error("Invalid input in full_pyramid.")
        return

def full_right_pyramid(line_num):
    if line_num > 0:
        pyr_base = 1 + ((line_num * 2) - 2)
        for lines in range(line_num):
            stars = 1 + (2 * lines)
            spaces = pyr_base - stars
            print(" " * spaces + "*" * stars)
    else:
        logger.error("Invalid input in full_right_pyramid.")
        return

def full_left_inverted_pyramid(line_num):
    if line_num > 0:
        for lines in range(line_num, 0, -1):
            stars = 1 + (2 * (lines - 1))
            print("*" * stars)
    else:
        logger.error("Invalid input in full_left_inverted_pyramid.")
        return

def full_inverted_pyramid(line_num):
    if line_num > 0:
        pyr_base = 1 + ((line_num * 2) - 2)
        for lines in range(line_num, 0, -1):
            stars = 1 + (2 * (lines - 1))
            spaces = (pyr_base - stars) // 2
            print(" " * spaces + "*" * stars)
    else:
        logger.error("Invalid input in full_inverted_pyramid.")
        return

def full_right_inverted_pyramid(line_num):
    if line_num > 0:
        pyr_base = 1 + ((line_num * 2) - 2)
        for lines in range(line_num, 0, -1):
            stars = 1 + (2 * (lines - 1))
            spaces = pyr_base - stars
            print(" " * spaces + "*" * stars)
    else:
        logger.error("Invalid input in full_right_inverted_pyramid.")
        return

def left_pyramid(line_num):
    if line_num > 0:
        for lines in range(line_num):
            stars = 1 + (2 * lines)
            if lines == line_num - 1:
                print("*" * stars)
            else:
                print("*" + " " * (stars - 2) + "*") if stars > 1 else print("*")
    else:
        logger.error("Invalid input in left_pyramid.")
        return

def pyramid(line_num):
    if line_num > 0:
        pyr_base = 1 + ((line_num * 2) - 2)
        for lines in range(line_num):
            stars = 1 + (2 * lines)
            spaces = (pyr_base - stars) // 2
            if lines == line_num - 1:
                print(" " * spaces + "*" * stars)
            else:
                if stars == 1:
                    print(" " * spaces + "*")
                else:
                    print(" " * spaces + "*" + " " * (stars - 2) + "*")
    else:
        logger.error("Invalid input in pyramid.")
        return

def right_pyramid(line_num):
    if line_num > 0:
        pyr_base = 1 + ((line_num * 2) - 2)
        for lines in range(line_num):
            stars = 1 + (2 * lines)
            spaces = pyr_base - stars
            if lines == line_num - 1:
                print(" " * spaces + "*" * stars)
            else:
                if stars == 1:
                    print(" " * spaces + "*")
                else:
                    print(" " * spaces + "*" + " " * (stars - 2) + "*")
    else:
        logger.error("Invalid input in right_pyramid.")
        return

def left_inverted_pyramid(line_num):
    if line_num > 0:
        for lines in range(line_num, 0, -1):
            stars = 1 + (2 * (lines - 1))
            if lines == line_num:
                print("*" * stars)
            else:
                print("*" + " " * (stars - 2) + "*") if stars > 1 else print("*")
    else:
        logger.error("Invalid input in left_inverted_pyramid.")
        return

def inverted_pyramid(line_num):
    if line_num > 0:
        pyr_base = 1 + ((line_num * 2) - 2)
        for lines in range(line_num, 0, -1):
            stars = 1 + (2 * (lines - 1))
            spaces = (pyr_base - stars) // 2
            if lines == line_num:
                print(" " * spaces + "*" * stars)
            else:
                if stars == 1:
                    print(" " * spaces + "*")
                else:
                    print(" " * spaces + "*" + " " * (stars - 2) + "*")
    else:
        logger.error("Invalid input in inverted_pyramid.")
        return

def right_inverted_pyramid(line_num):
    if line_num > 0:
        pyr_base = 1 + ((line_num * 2) - 2)
        for lines in range(line_num, 0, -1):
            stars = 1 + (2 * (lines - 1))
            spaces = pyr_base - stars
            if lines == line_num:
                print(" " * spaces + "*" * stars)
            else:
                if stars == 1:
                    print(" " * spaces + "*")
                else:
                    print(" " * spaces + "*" + " " * (stars - 2) + "*")
    else:
        logger.error("Invalid input in right_inverted_pyramid.")
        return

def number_pyramid(line_num):
    if line_num > 0:
        for i in range(1, line_num + 1):
            print(" " * (line_num - i), end="")
            for j in range(1, i + 1):
                print(f"{j} ", end="")
            print()
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

"""SQUARE-LIKE METHODS"""
def full_square(sides):
    if sides > 0:
        for _ in range(sides):
            print("*" * sides)
    else:
        logger.error("Invalid input in full_square.")
        return

def full_rectangle(width, height):
    if width > 0 and height > 0:
        for _ in range(height):
            print("*" * width)
    else:
        logger.error("Invalid input in full_rectangle.")
        return

def square(sides):
    if sides > 0:
        for row in range(sides):
            if row == 0 or row == sides - 1:
                print("*" * sides)
            else:
                print("*" + " " * (sides - 2) + "*")
    else:
        logger.error("Invalid input in square.")
        return

def rectangle(width, height):
    if width > 0 and height > 0:
        for row in range(height):
            if row == 0 or row == height - 1:
                print("*" * width)
            else:
                print("*" + " " * (width - 2) + "*")
    else:
        logger.error("Invalid input in rectangle.")
        return

"""TRIANGLES SHAPES"""
def pascals_triangle(line_num):
    if line_num > 0:
        for i in range(line_num):
            print(" " * (line_num - i), end="")
            val = 1
            for j in range(i + 1):
                print(f"{val} ", end="")
                val = val * (i - j) // (j + 1)
            print()
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def floyds_triangle(lines):
    if lines > 0:
        num = 1
        for i in range(1, lines + 1):
            for j in range(i):
                print(f"{num} ", end="")
                num += 1
            print()
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

"""DIAMOND-LIKE SHAPES"""
def diamond(line_num):
    if line_num > 0:
        for i in range(line_num):
            print(" " * (line_num - i - 1) + "*" * (2 * i + 1))
        for i in range(line_num - 2, -1, -1):
            print(" " * (line_num - i - 1) + "*" * (2 * i + 1))
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def half_diamond(line_num):
    if line_num > 0:
        for i in range(1, line_num + 1):
            print("*" * i)
        for i in range(line_num - 1, 0, -1):
            print("*" * i)
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def hollow_diamond(size):
    if size > 0:
        for i in range(size):
            for j in range(2 * size - 1):
                if j == size - 1 - i or j == size - 1 + i:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        for i in range(size - 2, -1, -1):
            for j in range(2 * size - 1):
                if j == size - 1 - i or j == size - 1 + i:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

"""SPECIAL SHAPES"""
def checkerboard(rows, cols):
    if rows > 0 and cols > 0:
        for i in range(rows):
            for j in range(cols):
                print("*" if (i + j) % 2 == 0 else " ", end="")
            print()
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def x_pattern(size):
    if size > 0:
        for i in range(size):
            for j in range(size):
                if i == j or j == size - 1 - i:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def zig_zag(rows):
    if rows > 0:
        for i in range(rows):
            for j in range(rows * 2):
                if (i + j) % 4 == 0:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def ascii_circle(radius):
    if radius > 0:
        for y in range(-radius, radius + 1):
            for x in range(-2 * radius, 2 * radius + 1):
                if x * x + 4 * y * y <= 4 * radius * radius:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def multiplication_table(n):
    if n > 0:
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                print(f"{i*j:4}", end="")
            print()
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def spiral_matrix(n):
    if n <= 0:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)
    matrix = [[0]*n for _ in range(n)]
    num = 1
    left, right, top, bottom = 0, n - 1, 0, n - 1
    while left <= right and top <= bottom:
        for i in range(left, right + 1):
            matrix[top][i] = num
            num += 1
        top += 1
        for i in range(top, bottom + 1):
            matrix[i][right] = num
            num += 1
        right -= 1
        for i in range(right, left - 1, -1):
            matrix[bottom][i] = num
            num += 1
        bottom -= 1
        for i in range(bottom, top - 1, -1):
            matrix[i][left] = num
            num += 1
        left += 1
    for row in matrix:
        print(" ".join(f"{v:2}" for v in row))

def heart_shape(size):
    if size > 0:
        for y in range(size//2, size, 1):
            for x in range(1, size*2):
                if ((x - size) ** 2 + (y - size//2) ** 2 <= (size//2)**2) or \
                   ((x - size//2) ** 2 + (y - size//2) ** 2 <= (size//2)**2):
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        for y in range(size):
            print(" " * y + "*" * ((size*2-1) - 2*y))
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def arrow(size):
    if size > 0:
        for i in range(size):
            print(" " * (size - i - 1) + "*" * (2 * i + 1))
        for i in range(size):
            print(" " * (size - 1) + "*")
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)

def hourglass(size):
    if size > 0:
        for i in range(size, 0, -1):
            spaces = size - i
            stars = 2 * i - 1
            print(" " * spaces + "*" * stars)
        for i in range(2, size + 1):
            spaces = size - i
            stars = 2 * i - 1
            print(" " * spaces + "*" * stars)
    else:
        print("Invalid input. Please enter positive integer(s).")
        sys.exit(1)
