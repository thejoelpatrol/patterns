import math
from abc import ABC, abstractmethod
import random
from enum import Enum
from typing import Tuple, List, Dict
from .utils import Bitmap, bytes_to_bits, generate_random_mask, generate_random_box_mask

DEBUG = True

class Doodler(ABC):

    def __init__(self, mask: Bitmap):
        if DEBUG:
            print(f"Doodler.__init__()")
        self.mask = mask
        self.width = self.mask.width
        self.height = self.mask.height
        self._image = Bitmap(self.width, self.height)
        self._generated = False
        self._masked = False
        if DEBUG:
            print(f"Doodler.__init__() done")

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
        if DEBUG:
            print("adding pattern masks")
        for pattern, mask in pattern_masks:
            mask.add(mask)
        super(PatternMultiDoodler, self).__init__(mask)
        self.pattern_masks = pattern_masks

    def _generate(self):
        if DEBUG:
            print("generating PatternMultiDoodler")
        for pattern, mask in self.pattern_masks:
            for y in range(self.height):
                for x in range(self.width):
                    if mask.pixels[y][x]:
                        pattern_y = y % pattern.height
                        pattern_x = x % pattern.width
                        self._image.pixels[y][x] = pattern.pixels[pattern_y][pattern_x]
        self._masked = True


class RandomPatternMultiDoodler(PatternMultiDoodler):
    MAX_FILL = 0.35

    def __init__(self, width: int, height: int, min_region_complexity: int, patterns: List[Bitmap], target_fill_fraction: float=0, max_fill_per_layer=MAX_FILL):
        masks = []
        for _ in range(len(patterns)):
            if DEBUG:
                print("generating random mask")
            mask = generate_random_mask(width, height, min_region_complexity, max_fill_per_layer - 0.1)
            masks.append(mask)
        if DEBUG:
            print("making bitmap mask")
        total_mask = Bitmap(width, height)
        for mask in masks:
            total_mask.add(mask)

        if DEBUG:
            print("filling masks")
        mask_iter = iter(masks)
        while total_mask.percent_filled < target_fill_fraction:
            print(total_mask.percent_filled)
            remaining_options = len(masks)
            for mask in masks:
                if mask.percent_filled > max_fill_per_layer:
                    remaining_options -= 1
            if remaining_options == 0:
                print("sorry")
                break

            try:
                mask = mask_iter.__next__()
                if mask.percent_filled > max_fill_per_layer:
                    continue
                region = generate_random_box_mask(width, height, overscan_x=200, overscan_y=200,
                                                    max_fill= 1.0 / math.sqrt(remaining_options))
                if region.intersects(mask):
                    mask.add(region)
                    total_mask.add(mask)
            except StopIteration:
                mask_iter = iter(masks)

        print(total_mask.percent_filled)
        random_pattern_masks = list(zip(patterns, masks))
        background_mask = Bitmap(width, height)
        background_mask.fill_black()
        random_pattern_masks.append( (random.sample(patterns, 1)[0], background_mask) )
        random_pattern_masks.reverse()
        super(RandomPatternMultiDoodler, self).__init__(random_pattern_masks)


class PatternPolygon(PatternDoodler):
    def __init__(self, width: int, height: int, pattern: Bitmap, stroked = True):
        self._gen_mask(width, height)
        self.stroked = stroked
        super(PatternPolygon, self).__init__(self.mask, pattern)

    @abstractmethod
    def _gen_mask(self, width: int, height: int):
        raise NotImplementedError()


class PatternTriangle(PatternPolygon):
    def _gen_mask(self, width: int, height: int):
        self.mask = Bitmap(width, height)
        self.vertices = list()
        for _ in range(3):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            self.vertices.append((x, y))
        for i in range(3):
            i_1 = (i + 1) % 3
            v1 = self.vertices[i]
            v2 = self.vertices[i_1]
            self.mask.fill_line(v1[0], v1[1], v2[0], v2[1])
        for y in range(self.mask.height):
            leftmost = None
            rightmost = None
            for x in range(self.mask.width):
                if self.mask.pixels[y][x]:
                    if not leftmost:
                        leftmost = x
                    rightmost = x
            if leftmost and rightmost:
                self.mask.fill_line(leftmost, y, rightmost, y)

    def _generate(self):
        super(PatternTriangle, self)._generate()
        if self.stroked:
            for i in range(3):
                i_1 = (i + 1) % 3
                self.image.fill_line(self.vertices[i][0], self.vertices[i][1], self.vertices[i_1][0], self.vertices[i_1][1])


class PatternRectangle(PatternPolygon):
    def _gen_mask(self, width: int, height: int):
        self.mask = Bitmap(width, height)
        self.x0 = random.randint(0, width - 1)
        self.y0 = random.randint(0, height - 1)
        self.x1 = random.randint(self.x0, width - 1)
        self.y1 = random.randint(self.y0, height - 1)
        for y in range(self.y0, self.y1 + 1):
            for x in range(self.x0, self.x1 + 1):
                self.mask.set(x, y)

    def _generate(self):
        super(PatternRectangle, self)._generate()
        if self.stroked:
            self.image.fill_line(self.x0, self.y0, self.x1, self.y0)
            self.image.fill_line(self.x0, self.y1, self.x1, self.y1)
            self.image.fill_line(self.x0, self.y0, self.x0, self.y1)
            self.image.fill_line(self.x1, self.y0, self.x1, self.y1)


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    @classmethod
    def increment(cls, direction: "Direction") -> Tuple[int, int]:
        INCREMENT = {cls.UP: (0,-1), cls.DOWN: (0,1), cls.LEFT: (-1,0), cls.RIGHT: (1,0)}
        return INCREMENT[direction]


class MaskSquiggler(Doodler):
    def __init__(self, mask: Bitmap, n_sqiggles: int, min_length: int = 1, max_length: int = 100, turn_propbability: float=0.1):
        super().__init__(mask)
        self.n_sqiggles = n_sqiggles
        self.min_length = min_length
        self.max_length = max_length
        self.turn_propbability = turn_propbability

    def _embellish(self, i: int, x: int, y: int, direction: Direction):
        pass

    def _generate(self):
        for i in range(self.n_sqiggles):
            direction = Direction(random.randint(0, 3))
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            len = random.randint(self.min_length, self.max_length)
            print(f"generating squiggle {i}")
            for i in range(len):
                self.image.set(x, y)
                increment = Direction.increment(direction)
                x += increment[0]
                y += increment[1]
                if x < 0:
                    x = 0
                if x >= self.width:
                    x = self.width - 1
                if y < 0:
                    y = 0
                if y >= self.height:
                    y = self.height - 1
                self._embellish(i, x, y, direction)
                if random.random() < self.turn_propbability:
                    direction = Direction(random.randint(0, 3))


class Squiggler(MaskSquiggler):
    def __init__(self, width: int, height: int, n_sqiggles: int, min_length: int = 1, max_length: int = 100, turn_propbability: float=0.1):
        mask = Bitmap(width, height)
        mask.fill_black()
        super().__init__(mask, n_sqiggles, min_length, max_length, turn_propbability)

    def _generate(self):
        super()._generate()
        self._masked = True


class TelegraphSquiggler(MaskSquiggler):
    def __init__(self, mask: Bitmap, n_sqiggles: int, min_length: int = 1, max_length: int = 100, turn_propbability: float = 0.1, cross_probability: float = 0.1):
        super().__init__(mask, n_sqiggles, min_length, max_length, turn_propbability)
        self.cross_probability = cross_probability
        self.just_set = False

    def _embellish(self, i: int, x: int, y: int, direction: Direction):
        if random.random() < self.cross_probability and not self.just_set:
            length = random.randint(1, 5)
            if direction in (Direction.UP, Direction.DOWN):
                for j in range(length):
                    self.image.set(x - j, y)
                    self.image.set(x + j, y)
            else:
                for j in range(length):
                    self.image.set(x, y - j)
                    self.image.set(x, y + j)
            self.just_set = True
        else:
            self.just_set = False



class NoiseMaskDoodler(Doodler):
    def __init__(self, mask: Bitmap, probability: float=0.1):
        super().__init__(mask)
        self.probability = probability

    def _generate(self):
        for x in range(self.width):
            for y in range(self.height):
                if random.random() < self.probability:
                    self.image.set(x, y)

class NoiseDoodler(NoiseMaskDoodler):
    def __init__(self, width: int, height: int, probability: float=0.1):
        mask = Bitmap(width, height)
        mask.fill_black()
        super().__init__(mask, probability)


class LineDoodler(Doodler):
    def __init__(self, mask: Bitmap, n_lines: int, max_dimension: int):
        super().__init__(mask)
        self.n_lines = n_lines
        self.max_dimension = max_dimension

    def _generate(self):
        for i in range(self.n_lines):
            x0 = random.randint(0, self.width - 1)
            y0 = random.randint(0, self.height - 1)
            if x0 > self.width / 2:
                x1 = random.randint(x0 - self.max_dimension, x0)
            else:
                x1 = random.randint(x0, x0 + self.max_dimension)
            if y0 > self.height / 2:
                y1 = random.randint(y0 - self.max_dimension, y0)
            else:
                y1 = random.randint(y0, y0 + self.max_dimension)
            self.image.fill_line(x0, y0, x1, y1)

# polygon masks
# roundrect masks

