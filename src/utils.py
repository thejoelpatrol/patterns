from __future__ import annotations
from typing import List, Union, Optional
import random

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

    def set(self, x: int, y: int):
        self.pixels[y][x] = 1
        self._pct_filled = None

    def clear(self, x: int, y: int):
        self.pixels[y][x] = 0
        self._pct_filled = None

    def fill_black(self):
        for y in range(self.height):
            for x in range(self.width):
                self.set(x, y)
        self._pct_filled = None

    def erase(self):
        for y in range(self.height):
            for x in range(self.width):
                self.clear(x, y)
        self._pct_filled = None

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