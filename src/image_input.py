from abc import ABC, abstractmethod
import png
from .utils import Bitmap


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


class MacpaintInput(ImageInput):
    @staticmethod
    def input(path: str) -> Bitmap:
        raise NotImplementedError()

