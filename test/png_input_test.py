import unittest
from typing import List
from patterns.src.image_input import PNGInput
from patterns.src.utils import Bitmap


class PNGInputTest(unittest.TestCase):
    def test_one_dot(self):
        p = PNGInput.input(path="test.png")

        correct = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                   [0, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                   [0, 1, 0, 1, 1, 0, 1, 1, 1, 0],
                   [0, 1, 1, 1, 0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
                   [0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
                   [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
                   [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        b = Bitmap(10, 10, correct)
        self.assertEqual(b, p)


if __name__ == '__main__':
    unittest.main()
