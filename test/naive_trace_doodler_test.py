import unittest
from typing import List
from patterns.src.doodler import OutlineDoodler, NaiveOutlineDoodler, NaiveTraceDoodler
from patterns.src.utils import Bitmap


class NaiveTraceDoodlerTests(unittest.TestCase):
    def test_one_dot(self):
        dot_mask = [[0, 0, 0],
                    [0, 1, 0],
                    [0, 0, 0]]
        outline = [[1, 1, 1],
                    [1, 0, 1],
                    [1, 1, 1]]
        mask = Bitmap(3,3,dot_mask)
        outline_result = Bitmap(3,3,outline)
        doodler = NaiveTraceDoodler(mask)
        doodler.generate()
        self.assertEqual(outline_result, doodler.image)

    def test_full(self):
        sq_mask = [[1, 1, 1],
                   [1, 1, 1],
                   [1, 1, 1]]
        outline = [[0, 0, 0],
                   [0, 0, 0],
                   [0, 0, 0]]
        mask = Bitmap(3,3,sq_mask)
        outline_result = Bitmap(3,3,outline)
        doodler = NaiveTraceDoodler(mask)
        doodler.generate()
        self.assertEqual(outline_result, doodler.image)

    def test_square_2x2(self):
        sq_mask = [[0, 0, 0, 0],
                   [0, 1, 1, 0],
                   [0, 1, 1, 0],
                   [0, 0, 0, 0]]
        outline_mask = [[1, 1, 1, 1],
                        [1, 0, 0, 1],
                        [1, 0, 0, 1],
                        [1, 1, 1, 1]]

        mask = Bitmap(4,4,sq_mask)
        outline_result = Bitmap(4,4,outline_mask)
        doodler = NaiveTraceDoodler(mask)
        doodler.generate()
        self.assertEqual(outline_result, doodler.image)

    def test_edge_square_2x2(self):
        sq_mask = [[1, 1, 0, 0],
                   [1, 1, 0, 0],
                   [0, 0, 0, 0],
                   [0, 0, 0, 0]]
        outline_mask = [[0, 0, 1, 0],
                        [0, 0, 1, 0],
                        [1, 1, 1, 0],
                        [0, 0, 0, 0]]

        mask = Bitmap(4,4,sq_mask)
        outline_result = Bitmap(4,4,outline_mask)
        doodler = NaiveTraceDoodler(mask)
        doodler.generate()
        self.assertEqual(outline_result, doodler.image)

    def test_square_3x3(self):
        sq_mask = [[0, 0, 0, 0, 0],
                   [0, 1, 1, 1, 0],
                   [0, 1, 1, 1, 0],
                   [0, 1, 1, 1, 0],
                   [0, 0, 0, 0, 0]]
        outline = [[1, 1, 1, 1, 1],
                   [1, 0, 0, 0, 1],
                   [1, 0, 0, 0, 1],
                   [1, 0, 0, 0, 1],
                   [1, 1, 1, 1, 1]]
        mask = Bitmap(5,5,sq_mask)
        outline_result = Bitmap(5,5,outline)
        doodler = NaiveTraceDoodler(mask)
        doodler.generate()
        self.assertEqual(outline_result, doodler.image)

    def test_complex_7x7(self):
        complex_mask = [[0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 1, 1, 0, 0, 0],
                        [0, 0, 1, 1, 1, 0, 0],
                        [0, 0, 0, 1, 1, 1, 0],
                        [0, 1, 1, 1, 1, 1, 0],
                        [0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0]]
        outline = [[0, 1, 1, 1, 1, 0, 0],
                   [0, 1, 0, 0, 1, 1, 0],
                   [0, 1, 0, 0, 0, 1, 1],
                   [1, 1, 1, 0, 0, 0, 1],
                   [1, 0, 0, 0, 0, 0, 1],
                   [1, 1, 1, 0, 1, 1, 1],
                   [0, 0, 1, 1, 1, 0, 0]]
        mask = Bitmap(7,7,complex_mask)
        outline_result = Bitmap(7,7,outline)
        doodler = NaiveTraceDoodler(mask)
        doodler.generate()
        self.assertEqual(outline_result, doodler.image)


if __name__ == '__main__':
    unittest.main()
