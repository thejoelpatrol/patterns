
from patterns.src.image_input import PNGInput
from patterns.src.image_output import PNGOutput
from patterns.src.utils import Bitmap
from patterns.src.doodler import NaiveTraceDoodler

bitmap = PNGInput.input("rect_mask.png")
outliner = NaiveTraceDoodler(bitmap)
outliner.generate()
PNGOutput.output(path="outline.png", bitmap=outliner.image)

bitmap = PNGInput.input("line.png")
outliner = NaiveTraceDoodler(bitmap)
outliner.generate()
PNGOutput.output(path="line_outline.png", bitmap=outliner.image)

bitmap = PNGInput.input("intersections.png")
outliner = NaiveTraceDoodler(bitmap)
outliner.generate()
PNGOutput.output(path="intersections_outlines.png", bitmap=outliner.image)
