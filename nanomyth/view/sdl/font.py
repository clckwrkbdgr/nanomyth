"""
Text-related functionality.
"""
import itertools
from ...math import Point

class FixedWidthFont:
	""" Pixel font with fixed width (monospace) glyphs.

	Should be loaded from font grid tileset where every letter has the same size.
	"""
	def __init__(self, tileset, letter_mapping):
		""" Creates font from tileset using given letter mapping.
		Letter mapping is a string of letters that should match unwrapped grid (row by row) starting from the topleft corner.
		Letter mapping could be shorted than overall size of the font tileset grid - unused tiles will be ignored.
		"""
		self.tileset = tileset
		tile_grid = itertools.chain.from_iterable((Point(x, y) for x in range(tileset.size.width)) for y in range(tileset.size.height))
		self.letter_mapping = dict(zip(letter_mapping, tile_grid))
	def get_letter_image(self, letter):
		""" Returns sub-image for given letter. """
		assert len(letter) == 1
		return self.tileset.get_tile(self.letter_mapping[letter])
