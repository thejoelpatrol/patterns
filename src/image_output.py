from abc import ABC, abstractmethod
import png
from .utils import Bitmap
from .macpaint_file.macpaint import MacPaintFile

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
        converted_data = []
        for row in bitmap.pixels:
            new_row = [255 if p == 0 else 0 for p in row]
            converted_data.append(new_row)
        macpaint = MacPaintFile.from_scanlines(converted_data)
        macpaint.write_file(path)
