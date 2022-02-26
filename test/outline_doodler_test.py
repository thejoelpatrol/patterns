import unittest
from typing import List
from patterns.src.doodler import OutlineDoodler
from patterns.src.utils import Bitmap


class OutlineDoodlerDotTest(unittest.TestCase):

    @unittest.skip("wikipedia algorithm does not work")
    def test_one_dot(self):
        dot_mask = [[0, 0, 0],
                    [0, 1, 0],
                    [0, 0, 0]]
        mask = Bitmap(3,3,dot_mask)
        doodler = OutlineDoodler(mask)
        doodler.generate()
        self.assertEqual(mask, doodler.mask)

    @unittest.skip("wikipedia algorithm does not work")
    def test_square(self):
        sq_mask = [[1, 1, 1],
                   [1, 1, 1],
                   [1, 1, 1]]
        outline = [[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]]
        mask = Bitmap(3,3,sq_mask)
        outline_result = Bitmap(3,3,outline)
        doodler = OutlineDoodler(mask)
        doodler.generate()
        self.assertEqual(outline_result, doodler.mask)

if __name__ == '__main__':
    unittest.main()
