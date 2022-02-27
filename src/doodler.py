from abc import ABC, abstractmethod
from .utils import Bitmap, bytes_to_bits
from typing import Tuple, List


class Doodler(ABC):

    def __init__(self, mask: Bitmap):
        self.mask = mask
        self.width = self.mask.width
        self.height = self.mask.height
        self._image = Bitmap(self.width, self.height)
        self._generated = False
        self._masked = False

    def generate(self) -> Bitmap:
        self._generated = True
        self._generate()
        if not self._masked:
            self._mask()
        return self._image

    @abstractmethod
    def _generate(self):
        raise NotImplementedError()

    def _mask(self):
        for y in range(self.height):
            for x in range(self.width):
                self._image.pixels[y][x] = self._image.pixels[y][x] & self.mask.pixels[y][x]
        self._masked = True

    @property
    def image(self) -> Bitmap:
        if not self._generated:
            raise RuntimeError("must call generate() before using image")
        return self._image


class NaiveOutlineDoodler(Doodler):

    def _neighbor_not_in_mask(self, x: int, y: int) -> bool:
        """
        preconditions: self.mask.pixels[y][x]
                    and 0 < x < self.mask.width - 1
                    and 0 < y < self.mask.height - 1
        :return:
        """
        if not self.mask.pixels[y-1][x]:
            return True
        if not self.mask.pixels[y + 1][x]:
            return True
        if not self.mask.pixels[y][x - 1]:
            return True
        if not self.mask.pixels[y][x + 1]:
            return True
        return False

    def _generate(self):
        for y in range(self.mask.height):
            for x in range(self.mask.width):
                if not self.mask.pixels[y][x]:
                    continue
                if x in (0, self.mask.width - 1):
                    self.image.set(x, y)
                    continue
                if y in (0, self.mask.height - 1):
                    self.image.set(x, y)
                    continue
                if self._neighbor_not_in_mask(x, y):
                    self.image.set(x, y)
        self._masked = True

class NaiveTraceDoodler(Doodler):

    def _neighbor_in_mask(self, x: int, y: int) -> bool:
        """
        preconditions: not self.mask.pixels[y][x]
        :return:
        """
        for _y in range(y - 1, y + 2):
            if _y < 0 or _y >= self.mask.height:
                continue
            for _x in range(x - 1, x + 2):
                if _x < 0 or _x >= self.mask.width:
                    continue
                if x == _x and y == _y:
                    continue
                if self.mask.pixels[_y][_x]:
                    return True
        return False

    def _generate(self):
        for y in range(self.mask.height):
            for x in range(self.mask.width):
                if self.mask.pixels[y][x]:
                    continue
                if self._neighbor_in_mask(x, y):
                    self.image.set(x, y)
        self._masked = True


class OutlineDoodler(Doodler):
    """
    https://en.wikipedia.org/wiki/Boundary_tracing#Square_tracing_algorithm
    """

    def _generate(self):
        self._begin_square_trace()
        self._masked = True

    def _begin_square_trace(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.mask.pixels[y][x]:
                    self._square_trace(x, y)
                    return

    def _go_left(self, point: Tuple[int, int]) -> Tuple[int, int]:
        return (point[1], -point[0])

    def _go_right(self, point: Tuple[int, int]) -> Tuple[int, int]:
        return (-point[1], point[0])

    def _square_trace(self, start_x: int, start_y: int):
        self._image.set(start_x, start_y)
        current = (start_x, start_y)
        first_move = self._go_left((1, 0))
        next_move = first_move
        current = (current[0] + next_move[0], current[1] + next_move[1])

        while current != (start_x, start_x) and next_move != first_move:
            current_x = current[0]
            current_y = current[1]
            if self.mask.pixels[current_y][current_x]:
                self._image.set(current_x, current_y)
                next_move = self._go_left(next_move)
                current = (current[0] + next_move[0], current[1] + next_move[1])
            else:
                current = (current[0] - next_move[0], current[1] - next_move[1])
                next_move = self._go_right(next_move)
                current = (current[0] + next_move[0], current[1] + next_move[1])


class ByteStringDoodler(Doodler):

    def __init__(self, mask: Bitmap, byte_string: bytes):
        super().__init__(mask)
        self.bitstring = bytes_to_bits(byte_string)

    def _generate(self):
        i = 0
        for y, row in enumerate(self.mask.pixels):
            for x, px in enumerate(row):
                if px:
                    self._image.pixels[y][x] = self.bitstring[i]
                    i += 1

        self._masked = True


class PatternDoodler(Doodler):

    def __init__(self, mask: Bitmap, pattern: Bitmap):
        super().__init__(mask)
        self.pattern = pattern

    def _generate(self):
        for y in range(self.height):
            for x in range(self.width):
                pattern_y = y % self.pattern.height
                pattern_x = x % self.pattern.width
                self._image.pixels[y][x] = self.pattern.pixels[pattern_y][pattern_x]


class PatternMultiDoodler(Doodler):

    def __init__(self, pattern_masks: List[Tuple[Bitmap, Bitmap]]):
        mask = Bitmap(pattern_masks[0][1].width, pattern_masks[0][0].height)
        for pattern, mask in pattern_masks:
            mask.add(mask)
        super(PatternMultiDoodler, self).__init__(mask)
        self.pattern_masks = pattern_masks

    def _generate(self):
        for pattern, mask in self.pattern_masks:
            for y in range(self.height):
                for x in range(self.width):
                    if mask.pixels[y][x]:
                        pattern_y = y % pattern.height
                        pattern_x = x % pattern.width
                        self._image.pixels[y][x] = pattern.pixels[pattern_y][pattern_x]
        self._masked = True
