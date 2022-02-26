from abc import ABC, abstractmethod
import png
from .utils import Bitmap


class ImageOutput(ABC):
    @staticmethod
    @abstractmethod
    def output(path: str, bitmap: Bitmap):
        raise NotImplementedError()


class PNGOutput(ImageOutput):
    @staticmethod
    def output(path: str, bitmap: Bitmap):
        rows = []
        for row in bitmap.pixels:
            rows.append([0 if p else 255 for p in row])
        with open(path, 'wb') as f:    # binary mode is important
            w = png.Writer(width=len(rows[0]), height=len(rows), greyscale=True)
            w.write(f, rows)


class MacpaintOutput(ImageOutput):
    @staticmethod
    def output(path: str, bitmap: Bitmap):
        raise NotImplementedError()
