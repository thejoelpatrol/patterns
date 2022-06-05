import os
from abc import ABC, abstractmethod
from typing import List

import png
from patterns.macpaint_file.macpaint import MacPaintFile
from patterns.src.utils import Bitmap


class ImageInput(ABC):
    @staticmethod
    @abstractmethod
    def input(path: str) -> Bitmap:
        raise NotImplementedError()


class PNGInput(ImageInput):
    @staticmethod
    def input(path: str) -> Bitmap:
        r = png.Reader(filename=path)
        width, height, rows, info = r.read()
        rows = list(rows)
        bitmap = Bitmap(width, height)
        for y in range(height):
            for x in range(width):
                if info['greyscale']:
                    px = rows[y][x]
                    if px == 0:
                        bitmap.set(x, y)
                else:
                    _x = x*3
                    px = rows[y][_x:_x+3]
                    if px == b"\x00\x00\x00":
                        bitmap.set(x, y)
        return bitmap

    @staticmethod
    def read_pattern_directory(path: str) -> List[Bitmap]:
        files = os.listdir(path)
        paths = []
        files.sort()
        for file in files:
            if file in [".", ".."]:
                continue
            paths.append(os.path.join(path, file))
        patterns = [PNGInput.input(file) for file in paths]
        return patterns

class MacPaintInput(ImageInput):
    @staticmethod
    def input(path: str) -> Bitmap:
        pntg = MacPaintFile.from_file(path)
        inverted_values = [
            [0 if p else 1 for p in row] for row in pntg.bitmap
        ]
        return Bitmap(pntg.WIDTH, pntg.HEIGHT, inverted_values)


