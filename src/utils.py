from __future__ import annotations
from typing import List, Union, Optional

class Bitmap:
    def __init__(self, width: int, height: int, pixels: Optional[List[List[int]]] = None):
        self.width = width
        self.height = height
        self.pixels = [] # type: List[List[int]]
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

    def set(self, x: int, y: int):
        self.pixels[y][x] = 1

    def clear(self, x: int, y: int):
        self.pixels[y][x] = 0

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
