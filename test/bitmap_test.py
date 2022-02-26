import unittest
from patterns.src.utils import Bitmap

class BitmapEqTest(unittest.TestCase):

    def test_eq_white_1px(self):
        img = [[False]]
        img2 = list(img)
        bitmap = Bitmap(1,1, img)
        bitmap2 = Bitmap(1,1,img2)
        self.assertEqual(bitmap, bitmap2)

    def test_eq_black_1px(self):
        img = [[True]]
        img2 = list(img)
        bitmap = Bitmap(1,1, img)
        bitmap2 = Bitmap(1,1,img2)
        self.assertEqual(bitmap, bitmap2)

    def test_eq_one_dot(self):
        img = [[False, False, False],
               [False, True, False],
               [False, False, False]]
        img2 = list(img)
        bitmap = Bitmap(3,3, img)
        bitmap2 = Bitmap(3,3,img2)
        self.assertEqual(bitmap, bitmap2)

    def test_eq_pattern(self):
        img = [[True, False, False],
               [False, True, True],
               [True, False, False]]
        img2 = list(img)
        bitmap = Bitmap(3,3, img)
        bitmap2 = Bitmap(3,3,img2)
        self.assertEqual(bitmap, bitmap2)

    def test_neq_one_px(self):
        img = [[False]]
        img2 = [[True]]
        bitmap = Bitmap(1,1, img)
        bitmap2 = Bitmap(1,1,img2)
        self.assertNotEqual(bitmap, bitmap2)

    def test_neq_one_dot(self):
        img = [[False, False, False],
               [False, True, False],
               [False, False, False]]
        img2 = [[False, False, False],
               [False, False, False],
               [False, False, False]]
        bitmap = Bitmap(3,3, img)
        bitmap2 = Bitmap(3,3,img2)
        self.assertNotEqual(bitmap, bitmap2)

    def test_neq_line(self):
        img = [[True, False, False],
               [False, True, False],
               [False, False, True]]
        img2 = [[False, False, True],
                [False, True, False],
                [True, False, False]]
        bitmap = Bitmap(3,3, img)
        bitmap2 = Bitmap(3,3,img2)
        self.assertNotEqual(bitmap, bitmap2)

    def test_neq_wrongsize(self):
        img = [[True, False, False],
               [False, True, False],
               [True, False, True]]
        img2 = [[True, False],
                [False, True],
                [True, False]]
        bitmap = Bitmap(3,3, img)
        bitmap2 = Bitmap(2,3,img2)
        self.assertNotEqual(bitmap, bitmap2)


class BitmapAddTest(unittest.TestCase):
    def test_add_blank(self):
        img = [[False, False, False],
               [False, False, False],
               [False, False, False]]
        img2 = list(img)
        bitmap = Bitmap(3,3, img)
        bitmap2 = Bitmap(3,3,img2)
        bitmap.add(bitmap2)
        self.assertEqual(bitmap, bitmap2)

    def test_add_dot(self):
        img = [[False, False, False],
               [False, False, False],
               [False, False, False]]
        img2 = [[False, False, False],
               [False, True, False],
               [False, False, False]]
        bitmap = Bitmap(3,3, img)
        bitmap2 = Bitmap(3,3,img2)
        bitmap.add(bitmap2)
        self.assertEqual(bitmap, bitmap2)

    def test_add_squares(self):
        img = [[True, True, False],
               [True, True, False],
               [False, False, False]]
        img2 = [[False, False, False],
                [False, True, True],
                [False, True, True]]
        combined = [[True, True, False],
                [True, True, True],
                [False, True, True]]
        bitmap = Bitmap(3,3, img)
        bitmap2 = Bitmap(3,3,img2)
        bitmap3 = Bitmap(3,3,combined)
        bitmap.add(bitmap2)
        self.assertEqual(bitmap, bitmap3)

if __name__ == '__main__':
    unittest.main()
