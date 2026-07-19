from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Union, Optional
import random

@dataclass
class Point:
    x: int
    y: int

@dataclass
class BoundingBox:
    upper_left: Point
    lower_right: Point

class Bitmap:
    def __init__(self, width: int, height: int, pixels: Optional[List[List[int]]] = None):
        self.width = width
        self.height = height
        self.pixels = [] # type: List[List[int]]
        self._pct_filled = None
        if pixels is None:
            for i in range(self.height):
                self.pixels.append([0] * self.width)
        else:
            self.pixels = list(pixels)

    def add(self, other: Bitmap):
        width = min(self.width, other.width)
        height = min(self.height, other.height)
        for y in range(height):
            for x in range(width):
                self.pixels[y][x] = self.pixels[y][x] | other.pixels[y][x]
        self._pct_filled = None

    def remove(self, other: Bitmap):
        if not self.intersects(other):
            return
        for y in range(min(other.height, self.height)):
            for x in range(min(other.width, self.width)):
                self.pixels[y][x] &= ~other.pixels[y][x]
        self.pct_filled = None

    def set(self, x: int, y: int):
        try:
            self.pixels[y][x] = 1
            self._pct_filled = None
        except IndexError:
            print(f"WARNING: tried to set ({y},{x}) out of bounds")

    def clear(self, x: int, y: int):
        self.pixels[y][x] = 0
        self._pct_filled = None

    def fill_black(self):
        for y in range(self.height):
            for x in range(self.width):
                self.set(x, y)
        self._pct_filled = 1.0

    def erase(self):
        for y in range(self.height):
            for x in range(self.width):
                self.clear(x, y)
        self._pct_filled = 0.0

    def invert(self):
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] ^= 1

    def scale(self, x_factor: int, y_factor: int) -> Bitmap:
        width = self.width * x_factor
        height = self.height * y_factor
        pixels = [] # type: List[List[int]]
        for i in range(height):
            pixels.append([0] * width)
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x]:
                    for j in range(y * y_factor, y * y_factor + y_factor):
                        for i in range(x * x_factor, x * x_factor + x_factor):
                            pixels[j][i] = 1
        return Bitmap(width, height, pixels)

    def intersects(self, other: Bitmap):
        for y in range(0, min(self.height, other.height)):
            for x in range(0, min(self.width, other.width)):
                if self.pixels[y][x] and other.pixels[y][x]:
                    return True

    @property
    def percent_filled(self) -> float:
        if self._pct_filled:
            return self._pct_filled
        filled = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x]:
                    filled += 1
        self._pct_filled = float(filled) / (self.width * self.height)
        return self._pct_filled

    def clone(self) -> Bitmap:
        new = Bitmap(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x]:
                    new.set(x, y)
        return new

    def fill_line(self, x0: int, y0: int, x1: int, y1: int):
        if x1 == x0:
            for y in range(y0, y1 + 1):
                self.set(x0, y)
        elif y1 == y0:
            for x in range(x0, x1 + 1):
                self.set(x, y0)
        else:
            # https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
            dx = abs(x1 - x0)
            sign_x = 1 if x0 < x1 else -1
            dy = -abs(y1 - y0)
            sign_y = 1 if y0 < y1 else -1
            error = dx + dy

            x = x0
            y = y0
            while True:
                self.set(x, y)
                e2 = 2 * error
                if e2 >= dy:
                    if x == x1:
                        break
                    error = error + dy
                    x = x + sign_x
                if e2 <= dx:
                    if y == y1:
                        break
                    error = error + dx
                    y = y + sign_y
        self.pct_filled = None

    def _ellipse_y(self, center_x: int, center_y: int, a: int, b: int, x: int, positive: bool) -> int :
        if x < center_x:
            start = x
            end = center_x
        else:
            start = center_x
            end = x
        translated_x = end - start
        y_squared = float( (a**2 * b**2) - (b**2 * translated_x**2) ) / a**2
        y = math.sqrt(y_squared)
        if positive:
            return int(round(y)) + center_y
        else:
            return -int(round(y)) + center_y

    def _ellipse_x(self, center_x: int, center_y: int, a: int, b: int, y: int, positive: bool) -> int :
        if y < center_y:
            start = y
            end = center_y
        else:
            start = center_y
            end = y
        translated_y = end - start
        x_squared = float( (a**2 * b**2) - (a**2 * translated_y**2) ) / b**2
        x = math.sqrt(x_squared)
        if positive:
            return int(round(x)) + center_x
        else:
            return -int(round(x)) + center_x

    def draw_arc(self, x0: int, y0: int, x1: int, y1: int, positive: bool):
        """
        precondition: x1 >= x0
        """
        if positive and y1 > y0:
            # upper left
            center_x = x1
            center_y = y0
            right = False
        elif not positive and y1 <= y0:
            # lower left
            center_x = x1
            center_y = y0
            right = False
        elif positive and  y1 <= y0:
            # upper right
            center_x = x0
            center_y = y1
            right = True
        elif not positive and  y1 > y0:
            # lower right
            center_x = x0
            center_y = y1
            right = True
        else:
            raise RuntimeError(f"wat? ({x0},{y0}) -> ({x1},{y1}")

        a = abs(x1 - x0)
        b = abs(y1 - y0)
        for x in range(x0, x1 + 1):
            y = self._ellipse_y(center_x, center_y, a, b, x, positive)
            self.set(x, y)
        # there might be a better way to handle vertical integer portions of the curve
        increment = 1 if y1 > y0 else -1
        for y in range(y0, y1 + increment, increment):
            x = self._ellipse_x(center_x, center_y, a, b, y, right)
            self.set(x, y)

    def draw_oval(self, x0: int, y0: int, x1: int, y1: int):
        x_mid = (x0 + x1) // 2
        y_mid = (y0 +  y1) // 2
        self.draw_arc(x0, y_mid, x_mid, y0, False)
        self.draw_arc(x_mid, y0, x1, y_mid, False)
        self.draw_arc(x0, y_mid, x_mid, y1, True)
        self.draw_arc(x_mid, y1, x1, y_mid, True)

    def __eq__(self, other: Bitmap):
        if self.width != other.width:
            return False
        if self.height != other.height:
            return False
        for i, row in enumerate(self.pixels):
            for j, p in enumerate(row):
                if p != other.pixels[i][j]:
                    return False
        return True

    def __str__(self):
        result = str()
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x]:
                    result += "#"
                else:
                    result += " "
            result += "\n"
        return result

    def draw_roundrect(self, bounds: BoundingBox, radius: int):
        upper_left = bounds.upper_left
        lower_right = bounds.lower_right
        upper_right = Point(bounds.lower_right.x, upper_left.y)
        lower_left = Point(bounds.upper_left.x, lower_right.y)

        upper_left_start = Point(upper_left.x, upper_left.y + radius - 1)
        upper_left_end = Point(upper_left.x + radius - 1, upper_left.y)
        upper_right_start = Point(upper_right.x - radius + 1, upper_right.y)
        upper_right_end = Point(upper_right.x, upper_left.y  + radius - 1)
        lower_left_start = Point(lower_left.x, lower_left.y - radius + 1)
        lower_left_end = Point(lower_left.x + radius - 1, lower_left.y)
        lower_right_start = Point(lower_right.x - radius + 1, lower_right.y)
        lower_right_end = Point(lower_right.x, lower_left.y - radius + 1)

        self.draw_arc(upper_left_start.x, upper_left_start.y, upper_left_end.x, upper_left_end.y, False)
        self.draw_arc(upper_right_start.x, upper_right_start.y, upper_right_end.x, upper_right_end.y, False)
        self.draw_arc(lower_left_start.x, lower_left_start.y, lower_left_end.x, lower_left_end.y, True)
        self.draw_arc(lower_right_start.x, lower_right_start.y, lower_right_end.x, lower_right_end.y, True)

        self.fill_line(upper_left_end.x, upper_left_end.y, upper_right_start.x, upper_right_start.y)
        self.fill_line(upper_left_start.x, upper_left_start.y, lower_left_start.x, lower_left_start.y)
        self.fill_line(lower_left_end.x, lower_left_end.y, lower_right_start.x, lower_right_start.y)
        self.fill_line(upper_right_end.x, upper_right_end.y, lower_right_end.x, lower_right_end.y)

    def fill_closed_shape(self, bounds: BoundingBox):
        for y in range(bounds.upper_left.y, bounds.lower_right.y):
            start = None
            end = None
            for x in range(bounds.upper_left.x, bounds.lower_right.x + 1):
                if not start and self.pixels[y][x]:
                    start = Point(x, y)
                if start and self.pixels[y][x]:
                    end = Point(x, y)
            self.fill_line(start.x, start.y, end.x, end.y)

def bytes_to_bits(buf: bytes) -> List[int]:
    result = []
    for b in buf:
        for i in range(8):
            mask = 1 << i
            bit = b & mask
            bit = bit >> i
            result.append(bit)
    return result

def generate_random_box_mask(width: int, height: int, overscan_x: int=200, overscan_y: int=200,
                             min_fill: float=0, max_fill: float=1.0) -> Bitmap:
    while True:
        col1 = random.randint(-1 * overscan_x, width / 2)
        col2 = random.randint(width / 2, width + overscan_x)
        row1 = random.randint(-1 * overscan_y, height / 2)
        row2 = random.randint(height / 2, height + overscan_y)
        mask = Bitmap(width, height)
        x1 = max(col1, 0)
        x2 = min(col2, width - 1)
        y1 = max(row1, 0)
        y2 = min(row2, height - 1)
        for y in range(y1, y2):
            for x in range(x1, x2):
                mask.set(x, y)
        pct_filled = mask.percent_filled
        if min_fill <= pct_filled <= max_fill:
            return mask

def generate_random_mask(width: int, height: int, target_regions: int, target_max_fill: float) -> Bitmap:
    mask = generate_random_box_mask(width, height, max_fill=0.20)
    for _ in range(target_regions - 1):
        region = generate_random_box_mask(width, height, max_fill=0.20)
        while (not mask.intersects(region)):
            region = generate_random_box_mask(width, height, max_fill=0.20)
        mask.add(region)
        if mask.percent_filled >= target_max_fill:
            break
    return mask