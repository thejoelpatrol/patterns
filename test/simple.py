
from patterns.src.image_input import PNGInput, MacPaintInput
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

bitmap = MacPaintInput.input("/Users/joel/Art/python/macpaint_file/venv/kigbobby#2")
outliner = NaiveTraceDoodler(bitmap)
outliner.generate()
PNGOutput.output(path="kigbobby2_outline2.png", bitmap=outliner.image)

for i in range(2, 6):
    bitmap = PNGInput.input(f"kigbobby2_outline{i}.png")
    outliner = NaiveTraceDoodler(bitmap)
    outliner.generate()
    PNGOutput.output(path=f"kigbobby2_outline{i+1}.png", bitmap=outliner.image)
